import sqlite3

def init_db():
    conn = sqlite3.connect('subscribers.db')
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
    conn.close()

def add_subscriber(email):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO subscribers (email, welcome_sent, ban) VALUES (?, 0, 0)', (email,))
    conn.commit()
    conn.close()
    print(f"Added subscriber: {email}")

def get_subscribers():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers WHERE ban = 0')
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    print(f"Fetched subscribers: {emails}")
    return emails

def mark_welcome_sent(email):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('UPDATE subscribers SET welcome_sent = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    print(f"Marked welcome sent for: {email}")

def get_new_subscribers():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers WHERE welcome_sent = 0 AND ban = 0')
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    print(f"Fetched new subscribers: {emails}")
    return emails

def ban_subscriber(email):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('UPDATE subscribers SET ban = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    print(f"Banned subscriber: {email}")

def add_admin_email(subject, date, body):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('INSERT INTO admin_emails (subject, date, body) VALUES (?, ?, ?)', (subject, date, body))
    conn.commit()
    conn.close()
    print(f"Added admin email: {subject} on {date}")

def admin_email_exists(subject, date, body):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM admin_emails WHERE subject = ? AND date = ? AND body = ?', (subject, date, body))
    exists = c.fetchone()[0] > 0
    conn.close()
    print(f"Admin email exists: {exists}")
    return exists
