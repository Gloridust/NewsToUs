import time
import schedule
from database import init_db
from email_handler import check_incoming_emails, handle_news_report
from datetime import datetime, timedelta, timezone

def main():
    init_db()
    check_incoming_emails()
    schedule.every().day.at("07:00").do(handle_news_report)
    schedule.run_pending()


if __name__ == '__main__':
    main()
