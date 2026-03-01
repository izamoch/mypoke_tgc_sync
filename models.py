from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class Set(Base):
    __tablename__ = "sets"

    id = Column(String, primary_key=True)
    name = Column(String)
    series = Column(String)
    card_count = Column(Integer)
    image_url = Column(String)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    cards = relationship("Card", back_populates="set")


class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True)
    name = Column(String)
    set_id = Column(String, ForeignKey("sets.id"))
    image_url = Column(String)
    phash = Column(String, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_price_check_at = Column(DateTime, default=None)

    set = relationship("Set", back_populates="cards")
    prices = relationship("CardPrice", back_populates="card")
    price_history = relationship("CardPriceHistory", back_populates="card", cascade="all, delete-orphan")


class CardPrice(Base):
    __tablename__ = "card_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey("cards.id"))
    price_type = Column(String)  # e.g., 'market', 'holofoil', 'reverseHolofoil'
    value = Column(Float)  # Market Price
    low = Column(Float)  # Low Price
    high = Column(Float)  # High Price
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    card = relationship("Card", back_populates="prices")


class CardPriceHistory(Base):
    __tablename__ = "card_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey("cards.id"))
    price_type = Column(String)  # Variant: 'normal', 'holofoil', etc.
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    value = Column(Float)  # Stores the HIGH price (or single tracked price)

    card = relationship("Card", back_populates="price_history")


class ChangeLog(Base):
    __tablename__ = "change_log"

    version_id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String)
    change_type = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(String)  # 'prices' or 'cards'
    status = Column(String)  # 'success' or 'error'
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
    cards_processed = Column(Integer, default=0)
    cards_added = Column(Integer, default=0)
    sets_added = Column(Integer, default=0)
    prices_updated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_details = Column(String)
