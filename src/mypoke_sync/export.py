import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from .models import Base, Set, Card, CardPrice

logger = logging.getLogger("sqlite_export")

def run_sqlite_export(supabase_url: str, sqlite_path: str = "./data/poke_tgc.sqlite"):
    """
    Replicates data from Supabase (PostgreSQL) to a local SQLite file.
    Always overwrites the local file for maximum simplicity and consistency.
    """
    logger.info(f"Starting simplified SQLite export to {sqlite_path}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    
    # Engines
    source_engine = create_engine(supabase_url)
    target_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # FRESH START: Drop and Create everything in SQLite
    logger.info("Dropping and recreating SQLite tables (Overwrite Strategy)...")
    Base.metadata.drop_all(target_engine)
    Base.metadata.create_all(target_engine)
    
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    with SourceSession() as src_db, TargetSession() as tgt_db:
        try:
            # 1. Sets
            logger.info("Copying 'sets'...")
            for s in src_db.query(Set).all():
                src_db.expunge(s)
                make_transient(s)
                tgt_db.add(s)
            tgt_db.commit()
            
            # 2. Cards
            logger.info("Copying 'cards'...")
            count_c = 0
            for card in src_db.query(Card).yield_per(1000):
                src_db.expunge(card)
                make_transient(card)
                tgt_db.add(card)
                count_c += 1
                if count_c % 2000 == 0:
                    tgt_db.commit()
            tgt_db.commit()
            
            # 3. Card Prices
            logger.info("Copying 'card_prices'...")
            count_p = 0
            for price in src_db.query(CardPrice).yield_per(2000):
                src_db.expunge(price)
                make_transient(price)
                tgt_db.add(price)
                count_p += 1
                if count_p % 5000 == 0:
                    tgt_db.commit()
            tgt_db.commit()
            
            logger.info(f"Done! Replicated {count_c} cards and {count_p} prices.")
            return True
            
        except Exception as e:
            tgt_db.rollback()
            logger.error(f"Export failed: {e}")
            raise
