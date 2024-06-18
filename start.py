import main
import time
from datetime import datetime, timedelta
import news_reporter
import email_handler
import config

sent_news_today = False

loop_times = 0
while True:
    loop_times = loop_times + 1
    print(f">>>loop {loop_times} start")
    print(f">>>main start")
    start_all = time.perf_counter()
    main.main()
    stop_main = time.perf_counter()
    print(f">>>news_reporter start")
    start_news_reporter = time.perf_counter()

    current_time = datetime.now()

    # 配置发送时间和结束时间
    send_time = current_time.replace(hour=config.news_send_hour, minute=config.news_send_min, second=0, microsecond=0)
    send_time_end = send_time + timedelta(minutes=5)

    # 检查是否在发送时间范围内
    if not sent_news_today and send_time <= current_time < send_time_end:
        output_html = news_reporter.main()
        subject = "NewsToUs:" + datetime.now().strftime('%Y-%m-%d')
        email_handler.send_newsletter(subject, output_html)
        sent_news_today = True
        print(f"news_reporter.main() 已在 {current_time.strftime('%Y-%m-%d %H:%M:%S')} 执行，sent_news_today 设为 True。")
        time.sleep(10)

    print(f">>>loop {loop_times} end")
    stop_all = time.perf_counter()
    print("main time:", stop_main - start_all)
    print("news_reporter time:", stop_all - start_news_reporter)
    print("All time:", stop_all - start_all)
    
    time.sleep(3)