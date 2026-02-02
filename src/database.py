from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    asset_id = Column(String, unique=True, nullable=False, index=True)  # Full nep141 asset ID
    chain = Column(String, nullable=True, index=True)  # eth, arb, base, etc.
    address = Column(String, nullable=True, index=True)  # Contract address
    
    __table_args__ = (
        UniqueConstraint('asset_id', name='uq_asset_id'),
    )

class BridgeTransaction(Base):
    __tablename__ = "bridge_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    token_in_id = Column(Integer, nullable=False, index=True)
    token_out_id = Column(Integer, nullable=False, index=True)
    amount_in = Column(Float, nullable=False)
    amount_out = Column(Float, nullable=False)
    slippage = Column(Float, nullable=False)
    deposit_address = Column(String, index=True)
    deposit_address_and_memo = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, index=True)
    intent_hash = Column(String, index=True)
    created_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('deposit_address_and_memo', name='uq_deposit_address_and_memo'),
    )

class SlippageCache(Base):
    __tablename__ = "slippage_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    token_in_id = Column(Integer, nullable=False, index=True)
    token_out_id = Column(Integer, nullable=False, index=True)
    avg_slippage = Column(Float)
    tx_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('token_in_id', 'token_out_id', name='uq_token_pair'),
    )

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
