import os
import psycopg2
import json
from typing import List
from .models import Account
from datetime import datetime
from typing import Any, Dict, List, Optional,Tuple
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db() -> None:
    try:
        conn = get_connection()
        cur = conn.cursor()
        print('initating token_store db',flush=True)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS token_store (
                realm_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_in INTEGER NOT NULL,
                issued_at DOUBLE PRECISION NOT NULL
            );
        """)
    
        conn.commit()
        conn.close()
        print('finished token_store db',flush=True)
    except Exception as e:
        raise e

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
    try:
        cur.execute("SELECT payload FROM accounts WHERE payload->>'Name' LIKE %s", (prefix + "%",))
        rows = cur.fetchall()
        conn.close()
        return [Account(**row[0]) for row in rows]
    except psycopg2.errors.UndefinedColumn:
        return []
    
def get_stored_token(user_token: str) -> Optional[Tuple[str, int, datetime]]:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute(
        """
        SELECT access_token, expires_in, issued_at
        FROM token_store
        WHERE access_token = %s
        LIMIT 1
        """,
        (user_token,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    access_token, expires_in, issued_at = row
    issued_at_dt = datetime.fromtimestamp(issued_at) if isinstance(issued_at, float) else issued_at
    return access_token, expires_in, issued_at_dt