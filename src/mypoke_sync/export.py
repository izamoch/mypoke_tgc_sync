import logging
import os
from sqlalchemy import create_engine, insert, event
from sqlalchemy.orm import sessionmaker
from .models import Base, Set, Card, CardPrice

logger = logging.getLogger("sqlite_export")

def _setup_sqlite_performance(dbapi_connection, connection_record):
    """
    Apply SQLite performance pragmas for faster bulk inserts.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA cache_size = 20000")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.close()

def run_sqlite_export(supabase_url: str, sqlite_path: str = "./data/poke_tgc.sqlite"):
    """
    Replicates data from Supabase (PostgreSQL) to a local SQLite file using BULK INSERTS.
    Always overwrites the local file for maximum simplicity and consistency.
    """
    logger.info(f"Starting optimized BULK SQLite export to {sqlite_path}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    
    # Engines
    source_engine = create_engine(supabase_url)
    # Important: SQLite dialect needs special handling for bulk in some versions, 
    # but SQLAlchemy core 'insert()' is generally fast.
    target_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # Apply performance pragmas to SQLite engine
    event.listen(target_engine, "connect", _setup_sqlite_performance)
    
    # FRESH START: Drop and Create everything in SQLite
    logger.info("Dropping and recreating SQLite tables (Overwrite Strategy)...")
    Base.metadata.drop_all(target_engine)
    Base.metadata.create_all(target_engine)
    
    SourceSession = sessionmaker(bind=source_engine)
    
    with SourceSession() as src_db:
        try:
            # 1. Sets (Small enough to do in one go)
            logger.info("Copying 'sets' (Bulk)...")
            all_sets = src_db.query(Set).all()
            if all_sets:
                set_dicts = [
                    {col.name: getattr(s, col.name) for col in Set.__table__.columns}
                    for s in all_sets
                ]
                with target_engine.begin() as conn:
                    conn.execute(insert(Set), set_dicts)
            
            # 2. Cards (Chunked to save memory)
            logger.info("Copying 'cards' (Bulk Chunked)...")
            count_c = 0
            chunk_size = 2000
            
            # Use offset/limit for stable chunking instead of yield_per for bulk
            while True:
                batch = src_db.query(Card).offset(count_c).limit(chunk_size).all()
                if not batch:
                    break
                
                card_dicts = [
                    {col.name: getattr(c, col.name) for col in Card.__table__.columns}
                    for c in batch
                ]
                with target_engine.begin() as conn:
                    conn.execute(insert(Card), card_dicts)
                
                count_c += len(batch)
                logger.info(f"  -> Progress: {count_c} cards...")

            # 3. Card Prices (Chunked)
            logger.info("Copying 'card_prices' (Bulk Chunked)...")
            count_p = 0
            chunk_size_p = 5000
            while True:
                batch_p = src_db.query(CardPrice).offset(count_p).limit(chunk_size_p).all()
                if not batch_p:
                    break
                
                price_dicts = [
                    {col.name: getattr(p, col.name) for col in CardPrice.__table__.columns}
                    for p in batch_p
                ]
                with target_engine.begin() as conn:
                    conn.execute(insert(CardPrice), price_dicts)
                
                count_p += len(batch_p)
                if count_p % 10000 == 0:
                    logger.info(f"  -> Progress: {count_p} prices...")
            
            logger.info(f"Done! Replicated {count_c} cards and {count_p} prices efficiently.")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
