"""
ClawReceipt Database Layer 🦞
Smart SQLite operations with tags, notes, search, and analytics support.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "receipts.db")


def _connect():
    """Create a DB connection with WAL mode for concurrent reads."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = _connect()
    c = conn.cursor()

    # Core receipts table
    c.execute('''CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT DEFAULT '',
                    store TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    tags TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now','localtime'))
                 )''')

    # Migrate: add new columns if they don't exist
    for col, default in [("time", "''"), ("notes", "''"), ("tags", "''"), ("created_at", "NULL")]:
        try:
            c.execute(f"ALTER TABLE receipts ADD COLUMN {col} TEXT DEFAULT {default}")
        except sqlite3.OperationalError:
            pass

    # Config table
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                 )''')

    # Category learning table (for smart categorization)
    c.execute('''CREATE TABLE IF NOT EXISTS category_learn (
                    store_pattern TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    updated_at TEXT DEFAULT (datetime('now','localtime'))
                 )''')

    # Default config
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('budget', '0.0')")

    # Create indexes for faster queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_receipts_date ON receipts(date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_receipts_store ON receipts(store)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_receipts_category ON receipts(category)")

    conn.commit()
    conn.close()


# ==============================
# 📝 RECEIPT CRUD
# ==============================

def add_receipt(date, time, store, amount, category, notes="", tags=""):
    """Add a receipt with optional notes and tags."""
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO receipts (date, time, store, amount, category, notes, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (date, time, store, amount, category, notes, tags)
    )
    receipt_id = c.lastrowid

    # Learn categorization pattern
    _learn_category(c, store, category)

    conn.commit()
    conn.close()
    return receipt_id


def update_receipt(receipt_id, **fields):
    """Update specific fields of a receipt."""
    allowed = {'date', 'time', 'store', 'amount', 'category', 'notes', 'tags'}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False

    conn = _connect()
    c = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [receipt_id]
    c.execute(f"UPDATE receipts SET {set_clause} WHERE id = ?", values)
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success


def delete_receipt(receipt_id):
    """Delete a receipt by ID."""
    conn = _connect()
    c = conn.cursor()
    c.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_receipt_by_id(receipt_id):
    """Get a single receipt by ID."""
    conn = _connect()
    df = pd.read_sql_query(
        "SELECT id, date, COALESCE(time,'') as time, store, amount, category, "
        "COALESCE(notes,'') as notes, COALESCE(tags,'') as tags FROM receipts WHERE id = ?",
        conn, params=(receipt_id,)
    )
    conn.close()
    return df.iloc[0] if not df.empty else None


def get_receipts(month=None):
    """Get receipts, optionally filtered by month (YYYY-MM)."""
    conn = _connect()
    base = ("SELECT id, date, COALESCE(time,'') as time, store, amount, category, "
            "COALESCE(notes,'') as notes, COALESCE(tags,'') as tags FROM receipts")
    if month:
        query = f"{base} WHERE date LIKE ? ORDER BY date DESC, id DESC"
        df = pd.read_sql_query(query, conn, params=(f"{month}%",))
    else:
        df = pd.read_sql_query(f"{base} ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df


# ==============================
# 💰 BUDGET & CONFIG
# ==============================

def get_budget():
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key='budget'")
    row = c.fetchone()
    conn.close()
    return float(row[0]) if row else 0.0


def set_budget(amount):
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('budget', ?)", (str(amount),))
    conn.commit()
    conn.close()


def get_config(key, default=None):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default


def set_config(key, value):
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


# ==============================
# 📊 ANALYTICS QUERIES
# ==============================

def get_total_spent(month=None):
    """Get total spent, optionally for a specific month (YYYY-MM)."""
    conn = _connect()
    c = conn.cursor()
    if month:
        c.execute("SELECT SUM(amount) FROM receipts WHERE date LIKE ?", (f"{month}%",))
    else:
        c.execute("SELECT SUM(amount) FROM receipts")
    row = c.fetchone()
    conn.close()
    return float(row[0] or 0.0)


def get_category_stats(month=None):
    """Get spending grouped by category."""
    conn = _connect()
    if month:
        query = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM receipts WHERE date LIKE ? GROUP BY category ORDER BY total DESC"
        df = pd.read_sql_query(query, conn, params=(f"{month}%",))
    else:
        query = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM receipts GROUP BY category ORDER BY total DESC"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_daily_spending(month=None):
    """Get daily spending totals."""
    conn = _connect()
    if month:
        query = "SELECT date, SUM(amount) as total, COUNT(*) as count FROM receipts WHERE date LIKE ? GROUP BY date ORDER BY date"
        df = pd.read_sql_query(query, conn, params=(f"{month}%",))
    else:
        query = "SELECT date, SUM(amount) as total, COUNT(*) as count FROM receipts GROUP BY date ORDER BY date"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_store_stats(month=None):
    """Get spending grouped by store."""
    conn = _connect()
    if month:
        query = "SELECT store, category, SUM(amount) as total, COUNT(*) as count FROM receipts WHERE date LIKE ? GROUP BY store, category ORDER BY total DESC"
        df = pd.read_sql_query(query, conn, params=(f"{month}%",))
    else:
        query = "SELECT store, category, SUM(amount) as total, COUNT(*) as count FROM receipts GROUP BY store, category ORDER BY total DESC"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_monthly_totals():
    """Get total spending per month for trend analysis."""
    conn = _connect()
    query = """
        SELECT substr(date, 1, 7) as month, 
               SUM(amount) as total, 
               COUNT(*) as count,
               AVG(amount) as avg_receipt
        FROM receipts 
        GROUP BY substr(date, 1, 7) 
        ORDER BY month
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def search_receipts_db(query_text):
    """Full-text search in database."""
    conn = _connect()
    like = f"%{query_text}%"
    df = pd.read_sql_query(
        "SELECT id, date, COALESCE(time,'') as time, store, amount, category, "
        "COALESCE(notes,'') as notes, COALESCE(tags,'') as tags "
        "FROM receipts WHERE store LIKE ? OR category LIKE ? OR notes LIKE ? OR tags LIKE ? OR date LIKE ? "
        "ORDER BY date DESC",
        conn, params=(like, like, like, like, like)
    )
    conn.close()
    return df


# ==============================
# 🧠 CATEGORY LEARNING
# ==============================

def _learn_category(cursor, store, category):
    """Store category association for future auto-suggest."""
    store_key = store.lower().strip()
    cursor.execute(
        "INSERT OR REPLACE INTO category_learn (store_pattern, category, confidence, updated_at) "
        "VALUES (?, ?, COALESCE((SELECT MIN(confidence + 0.1, 1.0) FROM category_learn WHERE store_pattern = ?), 0.5), datetime('now','localtime'))",
        (store_key, category, store_key)
    )


def get_learned_category(store):
    """Get the learned category for a store."""
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT category, confidence FROM category_learn WHERE store_pattern = ?", (store.lower().strip(),))
    row = c.fetchone()
    conn.close()
    if row:
        return {"category": row[0], "confidence": row[1]}
    return None


def get_all_categories():
    """Get all unique categories used."""
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM receipts ORDER BY category")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return cats


def get_all_stores():
    """Get all unique stores."""
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT DISTINCT store FROM receipts ORDER BY store")
    stores = [row[0] for row in c.fetchall()]
    conn.close()
    return stores


# ==============================
# 📤 EXPORT
# ==============================

def export_to_csv(filename):
    df = get_receipts()
    df.to_csv(filename, index=False)


def export_to_excel(filename):
    df = get_receipts()
    df.to_excel(filename, index=False)
