import main
import time
from datetime import datetime, timedelta
import news_reporter
import email_handler
import config

sent_news_today = {}

def initialize_sent_news():
    global sent_news_today
    today = datetime.now().date()
    sent_news_today = {f"{time_point['hour']}:{time_point['minute']}": False for time_point in config.news_send_times}

def check_and_send_news():
    global sent_news_today
    current_time = datetime.now()
    today = current_time.date()

    for time_point in config.news_send_times:
        send_time = current_time.replace(hour=time_point['hour'], minute=time_point['minute'], second=0, microsecond=0)
        send_time_end = send_time + timedelta(minutes=5)
        time_key = f"{time_point['hour']}:{time_point['minute']}"

        if not sent_news_today[time_key] and send_time <= current_time < send_time_end:
            output_html = news_reporter.main()
            subject = "NewsToUs:" + current_time.strftime('%Y-%m-%d')
            email_handler.send_newsletter(subject, output_html)
            sent_news_today[time_key] = True
            print(f"news_reporter.main() 已在 {current_time.strftime('%Y-%m-%d %H:%M:%S')} 执行，sent_news_today[{time_key}] 设为 True。")
            time.sleep(10)

loop_times = 0
initialize_sent_news()
last_reset_date = datetime.now().date()

while True:
    loop_times = loop_times + 1
    print(f">>>loop {loop_times} start")
    print(f">>>main start")
    start_all = time.perf_counter()
    main.main()
    stop_main = time.perf_counter()
    print(f">>>news_reporter start")
    start_news_reporter = time.perf_counter()

    current_date = datetime.now().date()
    if current_date != last_reset_date:
        initialize_sent_news()
        last_reset_date = current_date

    check_and_send_news()

    print(f">>>loop {loop_times} end")
    stop_all = time.perf_counter()
    print("main time:", stop_main - start_all)
    print("news_reporter time:", stop_all - start_news_reporter)
    print("All time:", stop_all - start_all)
    
    time.sleep(3)
