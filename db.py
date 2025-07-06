import sqlite3
from datetime import datetime

DB_NAME = "users.db"

# Create tables if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        filename TEXT,
        summary TEXT,
        timestamp TEXT
    )''')

    conn.commit()
    conn.close()

# Register user
def register_user(email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except:
        return False

# Login check
def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    return c.fetchone()

# Save upload history
def save_upload(email, filename, summary):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO uploads (user_email, filename, summary, timestamp) VALUES (?, ?, ?, ?)",
              (email, filename, summary, timestamp))
    conn.commit()
    conn.close()

# Fetch history
def get_user_history(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT filename, summary, timestamp FROM uploads WHERE user_email=? ORDER BY timestamp DESC", (email,))
    return c.fetchall()
