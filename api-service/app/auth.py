
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import secrets
import time
from typing import Optional

from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from .qb_client import save_tokens

router = APIRouter(prefix="/auth")


@router.get("/authorize", response_class=RedirectResponse)
def authorize() -> RedirectResponse:
    state: str = secrets.token_urlsafe(32)
    auth_url: str = (
        "https://appcenter.intuit.com/connect/oauth2"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri=http://localhost:8000/auth/callback"
        "&response_type=code"
        "&scope=com.intuit.quickbooks.accounting"
        f"&state={state}"
    )

    response = RedirectResponse(auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=False,    
        samesite="lax", 
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
    if not state or state != original_state:
        raise HTTPException(status_code=400, detail="Invalid or missing state parameter")

    token_url: str = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    resp = requests.post(
        token_url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": 'http://localhost:8000/auth/callback',
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

    response = JSONResponse({"status": "tokens_saved", "realmId": realmId})
    response.delete_cookie("oauth_state")
    return response
