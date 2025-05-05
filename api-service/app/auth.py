
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import secrets
import time
from typing import Optional,Tuple
from datetime import datetime, timedelta
from .db import get_stored_token
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,USE_UI
from .qb_client import save_tokens

router = APIRouter(prefix="/auth")
redirect_url = REDIRECT_URI if not USE_UI else "http://localhost:3000/auth/callback"

@router.get("/authorize", response_class=RedirectResponse)
def authorize() -> RedirectResponse:
    state: str = secrets.token_urlsafe(32)
    
    auth_url: str = (
        "https://appcenter.intuit.com/connect/oauth2"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={redirect_url}"
        "&response_type=code"
        "&scope=com.intuit.quickbooks.accounting"
        f"&state={state}"
    )

    response = RedirectResponse(auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=True
    )
    return response


@router.get("/callback")
def callback(
    request: Request,
    code: Optional[str] = None,
    realmId: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
) -> JSONResponse:
    if error:
        raise HTTPException(status_code=400, detail=error)

    original_state: Optional[str] = request.cookies.get("oauth_state")
    if not original_state:
        original_state = state #fallback for query params 
    
    if not state or state!=original_state:
        raise HTTPException(status_code=400, detail="Invalid or missing state parameter")

    token_url: str = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    resp = requests.post(
        token_url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_url,
        },
    )
    if resp.status_code != 200:   
        detail = resp.json() if resp.headers.get("Content-Type","").startswith("application/json") else resp.text
        return JSONResponse(
            status_code=resp.status_code,
            content={"error": "token_exchange_failed", "detail": detail}
        )

    tokens: dict = resp.json()  

    token_record = {
        "realmId":       realmId or "",
        "access_token":  tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_in":    tokens["expires_in"],
        "issued_at":     time.time(),
    }
    save_tokens(token_record)

    response = JSONResponse({"status": "tokens_saved",
                            "realmId": realmId,
                            "expires_in":tokens['expires_in'],
                            "access_token":tokens['access_token']})
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=True
    )
    return response

def is_token_valid(provided_token: str, stored: Tuple[str, int, datetime]) -> bool:
    stored_token, expires_in, issued_at = stored
    expiry_time = issued_at + timedelta(seconds=expires_in)
    return provided_token == stored_token and datetime.utcnow() < expiry_time

def require_valid_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    provided_token = auth_header.split(" ")[1]
    stored_token = get_stored_token(provided_token)
    if not stored_token or not is_token_valid(provided_token, stored_token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
