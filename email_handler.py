import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from email.header import decode_header
from config import SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT, ADMIN_EMAIL
from database import add_subscriber, get_subscribers, mark_welcome_sent, get_new_subscribers

def check_incoming_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()
    print(f"Found emails: {email_ids}")

    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        if result == 'OK':
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    email_message = BytesParser().parsebytes(raw_email)
                    
                    # 提取发件人地址
                    sender = email_message['From']
                    sender_email = None
                    if '<' in sender and '>' in sender:
                        sender_email = sender.split('<')[1].split('>')[0]
                    else:
                        sender_email = sender

                    print(f"Processing email from: {sender_email}")

                    if sender_email == ADMIN_EMAIL:
                        subject, encoding = decode_header(email_message['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8')
                        content = email_message.get_payload(decode=True).decode()
                        print(f"Admin email detected. Subject: {subject}")
                        send_newsletter(subject, content)
                    else:
                        add_subscriber(sender_email)
                        new_subscribers = get_new_subscribers()
                        if sender_email in new_subscribers:
                            try:
                                send_welcome_email(sender_email)
                                mark_welcome_sent(sender_email)
                            except smtplib.SMTPDataError as e:
                                print(f"Failed to send welcome email to {sender_email}: {e}")

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
        msg = MIMEMultipart()
        msg['From'] = SYSTEM_EMAIL
        msg['To'] = subscriber
        msg['Subject'] = subject
        
        body = MIMEText(content, 'plain')
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
