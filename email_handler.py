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

    mail.close()
    mail.logout()

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
