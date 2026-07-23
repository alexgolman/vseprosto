import sqlite3

DB_NAME = "cafe.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            card TEXT NOT NULL,
            items TEXT NOT NULL,
            status TEXT DEFAULT 'новый',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_menu_item(name, price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def get_menu():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM menu")
    items = cur.fetchall()
    conn.close()
    return items

def remove_menu_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM menu WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def add_order(client_name, card, items):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (client_name, card, items) VALUES (?, ?, ?)", (client_name, card, items))
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id

def get_orders():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, client_name, card, items, status, created_at FROM orders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_order_status(order_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_order_status(order_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None