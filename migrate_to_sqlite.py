import os
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Define the models exactly as they appear in models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# Source setup
SOURCE_URL = os.getenv("DATABASE_URL")
if SOURCE_URL and SOURCE_URL.startswith("postgres://"):
    SOURCE_URL = SOURCE_URL.replace("postgres://", "postgresql://", 1)

source_engine = create_engine(SOURCE_URL)

# Target setup
TARGET_URL = "sqlite:///./data/poketmon.sqlite"
target_engine = create_engine(TARGET_URL, connect_args={"check_same_thread": False})
TargetBase = declarative_base()

class Set(TargetBase):
    __tablename__ = "sets"
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    series = Column(String, index=True)
    card_count = Column(Integer)
    image_url = Column(String)
    release_date = Column(String)
    updated_at = Column(DateTime)
    cards = relationship("Card", back_populates="set")


class Card(TargetBase):
    __tablename__ = "cards"
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    set_id = Column(String, ForeignKey("sets.id"), index=True)
    image_url = Column(String)
    phash = Column(String, index=True)
    
    dex_id = Column(Integer, index=True)
    rarity = Column(String, index=True)
    category = Column(String, index=True)
    illustrator = Column(String, index=True)
    hp = Column(Integer)
    types = Column(String)
    stage = Column(String)
    suffix = Column(String)
    attacks = Column(String)
    weaknesses = Column(String)
    retreat = Column(Integer)
    regulation_mark = Column(String)
    legal = Column(String)
    flavor_text = Column(String)
    evolutions = Column(String)
    updated_at = Column(DateTime)
    last_price_check_at = Column(DateTime)
    
    set = relationship("Set", back_populates="cards")
    prices = relationship("CardPrice", back_populates="card")


class CardPrice(TargetBase):
    __tablename__ = "card_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey("cards.id"), index=True)
    price_type = Column(String, index=True)
    market = Column(Float)
    low = Column(Float)
    mid = Column(Float)
    high = Column(Float)
    direct = Column(Float)
    avg = Column(Float)
    trend = Column(Float)
    trend_1d = Column(Float)
    trend_7d = Column(Float)
    trend_30d = Column(Float)
    updated_at = Column(DateTime)
    card = relationship("Card", back_populates="prices")


def copy_table(source_engine, target_engine, target_table, chunk_size=1000):
    print(f"Copying {target_table.name}...")
    with source_engine.connect() as src_conn:
        with target_engine.begin() as tgt_conn:
            # We use core select to avoid ORM overhead
            query = select(target_table)
            result = src_conn.execute(query)
            
            rows = result.fetchall()
            if not rows:
                print(f"No data in source {target_table.name}")
                return
            
            keys = result.keys()
            data = [dict(zip(keys, row)) for row in rows]
            
            # Insert in chunks using Core
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                tgt_conn.execute(target_table.insert(), chunk)
                
            print(f"Inserted {len(data)} rows into {target_table.name}.")

if __name__ == "__main__":
    if os.path.exists("./data/poketmon.sqlite"):
        print("Removing existing sqlite db...")
        os.remove("./data/poketmon.sqlite")
        
    print("Creating schema in Target DB...")
    TargetBase.metadata.create_all(target_engine)
    
    # We load target tables one by one (Sets -> Cards -> Prices)
    copy_table(source_engine, target_engine, Set.__table__)
    copy_table(source_engine, target_engine, Card.__table__)
    copy_table(source_engine, target_engine, CardPrice.__table__)
    
    print("Migration complete!")
