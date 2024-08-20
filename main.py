import asyncio
import logging
from datetime import datetime, timedelta
import news_reporter
from email_handler import email_handler
from database import db_manager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_and_send_news():
    current_time = datetime.now()
    for time_point in config.news_send_times:
        send_time = current_time.replace(hour=time_point['hour'], minute=time_point['minute'], second=0, microsecond=0)
        if send_time <= current_time < send_time + timedelta(minutes=5):
            try:
                output_html = await news_reporter.main()
                subject = f"NewsToUs: {current_time.strftime('%Y-%m-%d')}"
                await email_handler.send_newsletter(subject, output_html)
                logging.info(f"新闻已发送: {subject}")
            except Exception as e:
                logging.error(f"发送新闻时出错: {e}")

async def main_loop():
    while True:
        try:
            await db_manager.init_db()
            await email_handler.check_incoming_emails()
            await check_and_send_news()
            await asyncio.sleep(60)  # 每分钟检查一次
        except Exception as e:
            logging.error(f"主循环出错: {e}")
            await asyncio.sleep(60)  # 出错后等待一分钟再重试

if __name__ == "__main__":
    asyncio.run(main_loop())