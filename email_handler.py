import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from email.header import decode_header
from email.utils import parsedate_to_datetime
from email.policy import default
from config import SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT, ADMIN_EMAIL
from database import add_subscriber, get_subscribers, mark_welcome_sent, get_new_subscribers, ban_subscriber, add_admin_email, admin_email_exists
from datetime import datetime, timedelta, timezone
import news_reporter

def check_incoming_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()
    print(f"Found emails: {email_ids}")

    latest_admin_email = None
    latest_admin_email_time = None

    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        if result == 'OK':
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    email_message = BytesParser(policy=default).parsebytes(raw_email)
                    
                    # 提取发件人地址
                    sender = email_message['From']
                    sender_email = None
                    if '<' in sender and '>' in sender:
                        sender_email = sender.split('<')[1].split('>')[0]
                    else:
                        sender_email = sender

                    print(f"Processing email from: {sender_email}")

                    # 提取邮件发送时间
                    email_date = email_message['Date']
                    email_datetime = parsedate_to_datetime(email_date).astimezone(timezone.utc)
                    print(f"Email received on: {email_datetime}")

                    if sender_email == ADMIN_EMAIL:
                        now = datetime.now(timezone.utc)
                        if email_datetime > now - timedelta(hours=12):
                            subject, encoding = decode_header(email_message['Subject'])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or 'utf-8')
                            content = get_email_body(email_message)
                            if not admin_email_exists(subject, email_datetime.isoformat(), content):
                                if latest_admin_email_time is None or email_datetime > latest_admin_email_time:
                                    latest_admin_email = email_message
                                    latest_admin_email_time = email_datetime
                    else:
                        add_subscriber(sender_email)
                        new_subscribers = get_new_subscribers()
                        if sender_email in new_subscribers:
                            try:
                                send_welcome_email(sender_email)
                                mark_welcome_sent(sender_email)
                            except smtplib.SMTPDataError as e:
                                print(f"Failed to send welcome email to {sender_email}: {e}")

    if latest_admin_email:
        subject, encoding = decode_header(latest_admin_email['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8')
        
        content = get_email_body(latest_admin_email)
        email_date = parsedate_to_datetime(latest_admin_email['Date']).astimezone(timezone.utc).isoformat()
        if not admin_email_exists(subject, email_date, content):
            add_admin_email(subject, email_date, content)
            print(f"Latest admin email detected. Subject: {subject}")
            send_newsletter(subject, content)

    mail.close()
    mail.logout()

def get_email_body(email_message):
    html_content = None
    text_content = None

    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                if content_type == "text/html":
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset())
                elif content_type == "text/plain":
                    text_content = part.get_payload(decode=True).decode(part.get_content_charset())

    else:
        if email_message.get_content_type() == "text/html":
            html_content = email_message.get_payload(decode=True).decode(email_message.get_content_charset())
        elif email_message.get_content_type() == "text/plain":
            text_content = email_message.get_payload(decode=True).decode(email_message.get_content_charset())

    return html_content if html_content else text_content

def send_welcome_email(subscriber_email):
    subject = "您好！您已成功注册 NewsToUs 服务！"
    body = "<p>感谢您注册我们的服务。您将会定期收到我们的新闻简报。</p>"

    msg = MIMEMultipart("alternative")
    msg['From'] = SYSTEM_EMAIL
    msg['To'] = subscriber_email
    msg['Subject'] = subject
    
    body_part = MIMEText(body, 'html')
    msg.attach(body_part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
        server.sendmail(SYSTEM_EMAIL, subscriber_email, msg.as_string())
        server.quit()
        print(f"Sent welcome email to: {subscriber_email}")
    except smtplib.SMTPDataError as e:
        print(f"Failed to send welcome email to {subscriber_email}: {e}")

def send_newsletter(subject, content):
    subscribers = get_subscribers()
    for subscriber in subscribers:
        msg = MIMEMultipart("alternative")
        msg['From'] = SYSTEM_EMAIL
        msg['To'] = subscriber
        msg['Subject'] = subject
        
        body = MIMEText(content, 'html') if content.startswith("<") else MIMEText(content, 'plain')
        msg.attach(body)

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
            server.sendmail(SYSTEM_EMAIL, subscriber, msg.as_string())
            server.quit()
            print(f"Sent newsletter to: {subscriber}")
        except smtplib.SMTPDataError as e:
            print(f"Failed to send email to {subscriber}: {e}")
            ban_subscriber(subscriber)

def handle_news_report():
    subject, output_html = news_reporter.main()  # Assuming news_reporter.main returns a subject and HTML content
    email_date = datetime.now(timezone.utc).isoformat()
    if not admin_email_exists(subject, email_date, output_html):
        add_admin_email(subject, email_date, output_html)
        print(f"Daily news report detected. Subject: {subject}")
        send_newsletter(subject, output_html)
