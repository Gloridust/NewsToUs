import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from email.header import decode_header
from email.utils import parsedate_to_datetime
from email.policy import default
from datetime import datetime, timedelta, timezone
import logging
from config import SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT, ADMIN_EMAIL
from database import db_manager

class EmailHandler:
    def __init__(self):
        self.db_manager = db_manager

    async def send_email(self, to_email, subject, content):
        msg = MIMEMultipart("alternative")
        msg['From'] = SYSTEM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html'))

        try:
            async with aiosmtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                await server.starttls()
                await server.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
                await server.send_message(msg)
            logging.info(f"发送邮件成功: {to_email}")
        except Exception as e:
            logging.error(f"发送邮件失败 {to_email}: {e}")
            await self.db_manager.ban_subscriber(to_email)

    async def send_welcome_email(self, subscriber_email):
        subject = "您好！您已成功注册 NewsToUs 服务！"
        body = "<p>感谢您注册我们的服务。您将会定期收到我们的新闻简报。</p>"
        await self.send_email(subscriber_email, subject, body)
        await self.db_manager.mark_welcome_sent(subscriber_email)

    async def send_newsletter(self, subject, content):
        subscribers = await self.db_manager.get_subscribers()
        tasks = [self.send_email(subscriber, subject, content) for subscriber in subscribers]
        await asyncio.gather(*tasks)

    async def check_incoming_emails(self):
        try:
            import aioimaplib
            client = aioimaplib.IMAP4_SSL(IMAP_SERVER)
            await client.wait_hello_from_server()
            await client.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
            await client.select('INBOX')
            _, data = await client.search('ALL')
            email_ids = data[0].split()
            logging.info(f"找到邮件: {len(email_ids)}")

            latest_admin_email = None
            latest_admin_email_time = None

            for email_id in email_ids:
                _, msg_data = await client.fetch(email_id, '(RFC822)')
                email_message = BytesParser(policy=default).parsebytes(msg_data[0][1])
                
                sender = email_message['From']
                sender_email = sender.split('<')[1].split('>')[0] if '<' in sender else sender

                logging.info(f"处理来自 {sender_email} 的邮件")

                email_datetime = parsedate_to_datetime(email_message['Date']).astimezone(timezone.utc)

                if sender_email == ADMIN_EMAIL:
                    now = datetime.now(timezone.utc)
                    if email_datetime > now - timedelta(hours=12):
                        subject = decode_header(email_message['Subject'])[0][0]
                        subject = subject.decode() if isinstance(subject, bytes) else subject
                        content = self.get_email_body(email_message)
                        if not await self.db_manager.admin_email_exists(subject, email_datetime.isoformat(), content):
                            if latest_admin_email_time is None or email_datetime > latest_admin_email_time:
                                latest_admin_email = email_message
                                latest_admin_email_time = email_datetime
                else:
                    await self.db_manager.add_subscriber(sender_email)
                    new_subscribers = await self.db_manager.get_new_subscribers()
                    if sender_email in new_subscribers:
                        await self.send_welcome_email(sender_email)

                await client.store(email_id, '+FLAGS', '\\Deleted')

            if latest_admin_email:
                subject = decode_header(latest_admin_email['Subject'])[0][0]
                subject = subject.decode() if isinstance(subject, bytes) else subject
                content = self.get_email_body(latest_admin_email)
                email_date = parsedate_to_datetime(latest_admin_email['Date']).astimezone(timezone.utc).isoformat()
                if not await self.db_manager.admin_email_exists(subject, email_date, content):
                    await self.db_manager.add_admin_email(subject, email_date, content)
                    logging.info(f"检测到最新管理员邮件. 主题: {subject}")
                    await self.send_newsletter(subject, content)

            await client.expunge()
            await client.logout()

        except Exception as e:
            logging.error(f"检查邮件时发生错误: {e}")

    def get_email_body(self, email_message):
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    return part.get_payload(decode=True).decode()
                elif content_type == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()

email_handler = EmailHandler()