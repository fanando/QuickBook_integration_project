import asyncio
from qb_client import get_accounts,has_tokens
from db_service import save_accounts_cache, init_db
from config import START_UP_PERIOD
fetch_period = 60 
async def periodic_crawl() -> None:
    server_init = False
    tokens_init = False
    
    while not server_init:
        try:
            init_db()
            server_init = True
        except Exception as e:
            await asyncio.sleep(START_UP_PERIOD)
    while not tokens_init:
        try:
            tokens_init = has_tokens()
        except Exception:
            print("waiting for user to authorize...",flush=True)
            await asyncio.sleep(fetch_period)
    while True:
        try:
            print("Fetching accounts from QBO...",flush=True)
            accounts = get_accounts(prefix="")
            print(f"Fetched {len(accounts)} accounts.",flush=True)
            save_accounts_cache(accounts)
            print("Accounts saved to DB.",flush=True)
        except Exception as e:
            print("Error during crawl:", e,flush=True)

        await asyncio.sleep(fetch_period)

if __name__ == "__main__":
    print("Starting crawler service...")
    asyncio.run(periodic_crawl())
