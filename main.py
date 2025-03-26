import requests
import time
from concurrent.futures import ThreadPoolExecutor

# إعدادات التحكم في عدد الطلبات في الثانية
MAX_REQUESTS_PER_SECOND = 1000
NUM_THREADS = 100  # عدد الخيوط (threads) لتوزيع العمل
REQUESTS_PER_THREAD = MAX_REQUESTS_PER_SECOND // NUM_THREADS  # توزيع الطلبات على الخيوط

# العنوان الذي سيتم إرسال الطلبات إليه
url = "https://dstat.countbot.uk/"

# دالة لإرسال الطلب
def send_request():
    try:
        response = requests.get(url)
        print(f"تم إرسال الطلب بنجاح. رمز الاستجابة: {response.status_code}")
    except requests.RequestException as e:
        print(f"حدث خطأ أثناء إرسال الطلب: {e}")

# دالة لتنفيذ الطلبات عبر الخيوط
def execute_requests():
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        while True:
            # إرسال مجموعة من الطلبات عبر الخيوط
            for _ in range(REQUESTS_PER_THREAD):
                executor.submit(send_request)
            # تأخير لتحديد المعدل المطلوب (إرسال 1000 طلب في الثانية)
            time.sleep(1)

if __name__ == "__main__":
    execute_requests()
