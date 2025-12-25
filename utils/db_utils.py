# utils/db_utils.py
import sqlite3
import os
from pathlib import Path
from datetime import datetime

from config import DB_PATH

def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    subtype TEXT,
                    details TEXT,
                    ts INTEGER NOT NULL
                )""")
    conn.commit()
    conn.close()

def insert_event(event_type, subtype=None, details=None, ts=None):
    ensure_db()
    if ts is None:
        ts = int(datetime.utcnow().timestamp())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO events (type, subtype, details, ts) VALUES (?, ?, ?, ?)",
              (event_type, subtype, details, ts))
    conn.commit()
    conn.close()

def fetch_events_since(ts_from):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, type, subtype, details, ts FROM events WHERE ts >= ? ORDER BY ts ASC", (ts_from,))
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_latest_event(event_type):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, type, subtype, details, ts FROM events WHERE type = ? ORDER BY ts DESC LIMIT 1", (event_type,))
    row = c.fetchone()
    conn.close()
    return row
