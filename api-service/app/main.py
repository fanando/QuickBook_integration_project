# app/main.py

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from .config import START_UP_PERIOD
from .auth import router as auth_router
from .models import Account
from .db import get_accounts, init_db, save_accounts_cache

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Accounts API Service")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.on_event("startup")
async def startup_event() -> None:
    db_ready = False
    while not db_ready:
        try:
            init_db()
            db_ready = True
        except Exception as e:
            print("Waiting for DB to be ready...", flush=True)
            await asyncio.sleep(START_UP_PERIOD)

    try:
        all_accounts = get_accounts(prefix="")
        save_accounts_cache(all_accounts)
    except Exception:
        pass

    async def _periodic_cache():
        while True:
            try:
                all_accounts = get_accounts(prefix="")
                save_accounts_cache(all_accounts)
            except Exception:
                pass
            await asyncio.sleep(3600)

    asyncio.create_task(_periodic_cache())

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        {"detail": "Too many requests, please try again later."},
        status_code=429
    )

app.include_router(auth_router)

@app.get("/accounts", response_model=list[Account])
@limiter.limit("10/minute")
def list_accounts(request: Request, prefix: str = "") -> list[Account]:
    return get_accounts(prefix)
