ADMIN_EMAIL = "admin@example.com"
SYSTEM_EMAIL = "system@example.com"
SYSTEM_EMAIL_PASSWORD = "your_password"
IMAP_SERVER = "imap.example.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587

ADMIN_EMAIL_HOURS_LIMIT = 12

news_send_times = [
    {"hour": 7, "minute": 00},
    {"hour": 13, "minute": 5},
    {"hour": 18, "minute": 00},]

# OpenAI
chat_url="https://apikeyplus.com/v1/chat/completions" #此处为中转URL，请更换为你自己的URL或官方URL
APIKEY=""