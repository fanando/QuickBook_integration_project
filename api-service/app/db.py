import os
import psycopg2
import json
from typing import List
from .models import Account
from datetime import datetime
from typing import Any, Dict, List, Optional
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db() -> None:
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS token_store (
                realm_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_in INTEGER NOT NULL,
                issued_at DOUBLE PRECISION NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        conn.commit()
        conn.close()
    except Exception as e:
        print("Failed to initialize api-service DB:", e, flush=True)

def save_accounts_cache(all_accounts: List[Dict[str, Any]]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow()
    for a in all_accounts:
        cur.execute("""
            INSERT INTO accounts (id, payload, cached_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
              payload = EXCLUDED.payload,
              cached_at = EXCLUDED.cached_at;
        """, (
            a["Id"],
            json.dumps(a),
            now,
        ))
    conn.commit()
    conn.close()


def get_accounts(prefix: str = "") -> List[Account]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT payload FROM accounts WHERE payload->>'Name' LIKE %s", (prefix + "%",))
    rows = cur.fetchall()
    conn.close()
    return [Account(**row[0]) for row in rows]
