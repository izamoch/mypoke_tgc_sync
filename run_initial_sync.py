import asyncio
import sync
from database import SessionLocal

async def main():
    db = SessionLocal()
    sync.start_sync_flag()
    try:
        print("Starting Initial Full Sync locally...")
        await sync.sync_sets_and_cards(db)
        if not sync.SHOULD_STOP:
             await sync.sync_prices(db)
        print("Initial Sync completed successfully.")
    except Exception as e:
        print(f"Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
