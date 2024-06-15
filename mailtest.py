import imaplib
from config import SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD, IMAP_SERVER, IMAP_PORT, SMTP_SERVER, SMTP_PORT

try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    print("Login successful")
    mail.logout()
except imaplib.IMAP4.error as e:
    print(f"Login failed: {e}")
