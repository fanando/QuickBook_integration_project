import psycopg2
import time
import requests
from typing import Any, Dict, List, Optional
import os
from config import QBO_SANDBOX_BASE, CLIENT_ID, CLIENT_SECRET

_TOKEN_TABLE = "token_store"

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def load_tokens() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT realm_id, access_token, refresh_token, expires_in, issued_at
        FROM { _TOKEN_TABLE }
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    if not row:
        return None

    realm_id, access, refresh, expires_in, issued_at = row
    return {
        "realmId": realm_id,
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": expires_in,
        "issued_at": issued_at,
    }

def has_tokens() -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM token_store LIMIT 1")
    result = cur.fetchone()
    conn.close()
    return result is not None


def save_tokens(tokens: Dict[str, Any]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM { _TOKEN_TABLE } WHERE realm_id = %s", (tokens["realmId"],))
    cur.execute(f"""
        INSERT INTO { _TOKEN_TABLE }
        (realm_id, access_token, refresh_token, expires_in, issued_at)
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

def ensure_token() -> Dict[str, Any]:
    tokens = load_tokens()
    if tokens is None:
        raise RuntimeError("No tokens found—please complete OAuth flow via /auth/authorize")

    now = time.time()
    if now > tokens["issued_at"] + tokens["expires_in"] - 60:
        refresh_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        auth = (CLIENT_ID, CLIENT_SECRET)
        data = {
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        }
        resp = requests.post(refresh_url, auth=auth, data=data)
        resp.raise_for_status()
        new = resp.json()
        new_tokens = {
            "realmId": tokens["realmId"],
            "access_token": new["access_token"],
            "refresh_token": new["refresh_token"],
            "expires_in": new["expires_in"],
            "issued_at": now,
        }
        save_tokens(new_tokens)
        return new_tokens

    return tokens

def get_accounts(prefix: str = "") -> List[Dict[str, Any]]:
    tokens = ensure_token()
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Accept": "application/json",
    }
    realm = tokens["realmId"]
    query = f"select * from Account where Name like '{prefix}%'"
    url = f"{QBO_SANDBOX_BASE}/v3/company/{realm}/query?query={query}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("QueryResponse", {}).get("Account", [])
