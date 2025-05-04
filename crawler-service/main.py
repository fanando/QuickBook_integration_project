import asyncio
from qb_client import get_accounts
from db_service import save_accounts_cache, init_db

async def periodic_crawl() -> None:
    try:
        print("Initializing DB...",flush=True)
        init_db()
        print("DB initialized.")
    except Exception as e:
        print("Failed to initialize DB:", e)
    while True:
        try:
            print("Fetching accounts from QBO...")
            accounts = get_accounts(prefix="")
            print(f"Fetched {len(accounts)} accounts.")
            save_accounts_cache(accounts)
            print("Accounts saved to DB.")
        except Exception as e:
            print("Error during crawl:", e)

        await asyncio.sleep(3600)

if __name__ == "__main__":
    print("Starting crawler service...")
    asyncio.run(periodic_crawl())
