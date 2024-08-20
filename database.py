import sqlite3
from contextlib import contextmanager
import logging

class DatabaseManager:
    def __init__(self, db_name='subscribers.db'):
        self.db_name = db_name

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    welcome_sent BOOLEAN NOT NULL DEFAULT 0,
                    ban BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS admin_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    date TEXT NOT NULL,
                    body TEXT NOT NULL
                )
            ''')
            conn.commit()
        logging.info("数据库初始化完成")

    def add_subscriber(self, email):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO subscribers (email, welcome_sent, ban) VALUES (?, 0, 0)', (email,))
            conn.commit()
        logging.info(f"添加订阅者: {email}")

    def get_subscribers(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT email FROM subscribers WHERE ban = 0')
            emails = [row[0] for row in c.fetchall()]
        logging.info(f"获取订阅者数量: {len(emails)}")
        return emails

    def mark_welcome_sent(self, email):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE subscribers SET welcome_sent = 1 WHERE email = ?', (email,))
            conn.commit()
        logging.info(f"标记欢迎邮件已发送: {email}")

    def get_new_subscribers(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT email FROM subscribers WHERE welcome_sent = 0 AND ban = 0')
            emails = [row[0] for row in c.fetchall()]
        logging.info(f"获取新订阅者数量: {len(emails)}")
        return emails

    def ban_subscriber(self, email):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE subscribers SET ban = 1 WHERE email = ?', (email,))
            conn.commit()
        logging.info(f"封禁订阅者: {email}")

    def add_admin_email(self, subject, date, body):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO admin_emails (subject, date, body) VALUES (?, ?, ?)', (subject, date, body))
            conn.commit()
        logging.info(f"添加管理员邮件: {subject} on {date}")

    def admin_email_exists(self, subject, date, body):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM admin_emails WHERE subject = ? AND date = ? AND body = ?', (subject, date, body))
            exists = c.fetchone()[0] > 0
        logging.info(f"管理员邮件存在: {exists}")
        return exists

db_manager = DatabaseManager()