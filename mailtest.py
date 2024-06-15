import imaplib

SYSTEM_EMAIL = "bot@newsto.us"
SYSTEM_EMAIL_PASSWORD = "yungeeker!2019"
IMAP_SERVER = "imap.qiye.aliyun.com"

try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(SYSTEM_EMAIL, SYSTEM_EMAIL_PASSWORD)
    print("Login successful")
    mail.logout()
except imaplib.IMAP4.error as e:
    print(f"Login failed: {e}")
