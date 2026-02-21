import asyncio
import logging
import sys
import argparse
from datetime import datetime

# Import database and sync modules
from database import SessionLocal
import sync
import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("sync_job")

async def run_sync_job(force_prices: bool = False):
    """
    Main entry point for the scheduled synchronization job.
    """
    start_time = datetime.utcnow()
    logger.info(f"Starting scheduled PokeTCG Sync Job at {start_time} (UTC)")
    
    db = SessionLocal()
    sync.start_sync_flag()

    try:
        # Step 1: Sync Sets and New Cards
        logger.info("Executing Phase 1: Sets and Cards synchronization...")
        await sync.sync_sets_and_cards(db)
        
        if sync.SHOULD_STOP:
            logger.warning("Sync stopped prematurely during Cards phase. Exiting.")
            return

        # Step 2: Sync Prices based on Temperature Strategy
        logger.info("Executing Phase 2: Price synchronization...")
        await sync.sync_prices(db)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Sync Job completed successfully in {duration:.1f} seconds.")

    except Exception as e:
        logger.error(f"Fatal error during sync job execution: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pokemon TCG Backend Synchronization Job")
    args = parser.parse_args()
    
    logger.info("Initializing Sync Job environment...")
    asyncio.run(run_sync_job())
