import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from config import SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT, ADMIN_EMAIL
from database import add_subscriber, get_subscribers

def check_incoming_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()
    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)
        
        sender = email_message['From']
        if sender == ADMIN_EMAIL:
            content = email_message.get_payload(decode=True).decode()
            send_newsletter(content)
        else:
            add_subscriber(sender)
            send_welcome_email(sender)

    mail.close()
    mail.logout()

def send_welcome_email(subscriber_email):
    subject = "您好！您已成功注册 Mail my news 服务！"
    body = "感谢您注册我们的服务。您将会定期收到我们的新闻简报。"

    msg = MIMEMultipart()
    msg['From'] = SYSTEM_EMAIL
    msg['To'] = subscriber_email
    msg['Subject'] = subject
    
    body_part = MIMEText(body, 'plain')
    msg.attach(body_part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    server.sendmail(SYSTEM_EMAIL, subscriber_email, msg.as_string())
    server.quit()

def send_newsletter(content):
    subscribers = get_subscribers()
    for subscriber in subscribers:
        msg = MIMEMultipart()
        msg['From'] = SYSTEM_EMAIL
        msg['To'] = subscriber
        msg['Subject'] = "Newsletter"
        
        body = MIMEText(content, 'plain')
        msg.attach(body)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
        server.sendmail(SYSTEM_EMAIL, subscriber, msg.as_string())
        server.quit()
