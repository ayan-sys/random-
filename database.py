import sqlite3
import datetime
import json

DB_NAME = "starbucks.db"

def init_db():
    """Initialize the database with users and orders tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, stars INTEGER, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, items TEXT, total REAL, date TEXT)''')
    conn.commit()
    conn.close()

def get_user(username):
    """Retrieve user details by username."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username):
    """Create a new user with 0 stars."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, 0, date))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # User already exists
    conn.close()

def update_stars(username, amount):
    """Add stars to a user's balance."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET stars = stars + ? WHERE username = ?", (amount, username))
    conn.commit()
    conn.close()

def add_order(username, items, total):
    """Record a new order."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Store items list as JSON string
    items_json = json.dumps(items)
    c.execute("INSERT INTO orders (username, items, total, date) VALUES (?, ?, ?, ?)", (username, items_json, total, date))
    conn.commit()
    conn.close()

def get_last_order(username):
    """Get the user's most recent order items."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT items FROM orders WHERE username=? ORDER BY id DESC LIMIT 1", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return None
