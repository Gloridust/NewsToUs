import sqlite3

def init_db():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            welcome_sent BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_subscriber(email):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO subscribers (email, welcome_sent) VALUES (?, 0)', (email,))
    conn.commit()
    conn.close()
    print(f"Added subscriber: {email}")

def get_subscribers():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers')
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
    c.execute('SELECT email FROM subscribers WHERE welcome_sent = 0')
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    print(f"Fetched new subscribers: {emails}")
    return emails
