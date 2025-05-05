import psycopg2
import json
import time
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db() -> None:
    try:
        conn = get_connection()
        
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                payload JSONB NOT NULL,
                cached_at DOUBLE PRECISION NOT NULL
            );
        """)
        conn.commit()
        conn.close()
        print("DB initialized.",flush=True)
    except Exception as e:
        print("Failed to initialize DB:", e,flush=True)
        raise e

def load_tokens() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT realm_id, access_token, refresh_token, expires_in, issued_at
        FROM token_store
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    realm, at, rt, exp, issued = row
    return {
        "realmId": realm,
        "access_token": at,
        "refresh_token": rt,
        "expires_in": exp,
        "issued_at": issued,
    }

def save_tokens(tokens: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM token_store WHERE realm_id = %s", (tokens["realmId"],))
    cur.execute("""
        INSERT INTO token_store (realm_id, access_token, refresh_token, expires_in, issued_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        tokens["realmId"],
        tokens["access_token"],
        tokens["refresh_token"],
        tokens["expires_in"],
        tokens["issued_at"],
    ))
    conn.commit()
    conn.close()

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

def load_accounts_cache(prefix: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT payload FROM accounts
        WHERE payload->>'Name' LIKE %s
    """, (prefix + "%",))
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]
