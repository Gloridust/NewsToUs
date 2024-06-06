import sqlite3

def init_db():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_subscriber(email):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO subscribers (email) VALUES (?)', (email,))
    conn.commit()
    conn.close()

def get_subscribers():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers')
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    return emails
