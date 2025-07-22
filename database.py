import sqlite3
from contextlib import contextmanager

DB_NAME = "pmpcs.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                requested_amount DECIMAL,
                currency TEXT,
                recipient_id TEXT,
                description TEXT,
                preferences JSON,
                status TEXT DEFAULT 'pending',
                paid_amount DECIMAL DEFAULT 0,
                expiry_timestamp DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT,
                type TEXT,
                payload BLOB,
                transaction_proof TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        conn.commit()



import uuid
import json
from datetime import datetime

def create_session(data):
    session_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, requested_amount, currency, recipient_id, description, preferences, expiry_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, data['amount'], data['currency'], data['recipient_id'], data['description'], json.dumps(data['preferences']), data['expiry']))
        conn.commit()
    return session_id

def get_session(session_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return {
                "session_id": row[0], "requested_amount": row[1], "currency": row[2],
                "recipient_id": row[3], "description": row[4], "preferences": json.loads(row[5]),
                "status": row[6], "paid_amount": row[7], "expiry_timestamp": row[8], "created_at": row[9]
            }
    return None
