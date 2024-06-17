import main
import time
import datetime
import news_reporter

sent_news_today = False

loop_times = 0
while True:
    loop_times = loop_times + 1
    print(f">>>loop {loop_times} start")
    print(f">>>main start")

    main.main()

    print(f">>>news_reporter start")

    current_time = datetime.datetime.now()
    
    # 如果当前时间是23:59，重置 sent_news_today
    if current_time.hour == 23 and current_time.minute == 59:
        sent_news_today = False
        print("sent_news_today 已重置为 False")
    
    # 如果 sent_news_today 为 False 且当前时间是 16:30，执行 news_reporter.main() 并设置 sent_news_today 为 True
    if not sent_news_today and current_time.hour == 16 and current_time.minute == 30:
        news_reporter.main()
        sent_news_today = True
        print(f"news_reporter.main() 已在 {current_time.strftime('%Y-%m-%d %H:%M:%S')} 执行，sent_news_today 设为 True。")
        time.sleep(30)

    print(f">>>loop {loop_times} end")
    time.sleep(10)