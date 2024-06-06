from database import init_db
from email_handler import check_incoming_emails

def main():
    init_db()
    check_incoming_emails()

if __name__ == '__main__':
    main()
