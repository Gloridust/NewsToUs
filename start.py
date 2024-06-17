import main
import time
from datetime import datetime
import news_reporter
import email_handler

sent_news_today = False

loop_times = 0
while True:
    loop_times = loop_times + 1
    print(f">>>loop {loop_times} start")
    print(f">>>main start")

    main.main()

    print(f">>>news_reporter start")

    current_time = datetime.now()
    
    # 如果当前时间是23:59，重置 sent_news_today
    if current_time.hour == 23 and current_time.minute == 59:
        sent_news_today = False
        print("sent_news_today 已重置为 False")
    
    # 如果 sent_news_today 为 False 且当前时间是 XX:XX，执行 news_reporter.main() 并设置 sent_news_today 为 True
    if not sent_news_today and current_time.hour == 16 and current_time.minute == 40:
        output_html=news_reporter.main()
        subject="NewsToUs:"+datetime.now().strftime('%Y-%m-%d')
        email_handler.send_newsletter(subject, output_html)
        sent_news_today = True
        print(f"news_reporter.main() 已在 {current_time.strftime('%Y-%m-%d %H:%M:%S')} 执行，sent_news_today 设为 True。")
        time.sleep(10)

    print(f">>>loop {loop_times} end")
    time.sleep(5)