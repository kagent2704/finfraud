# backend/app/db/models.py
from sqlalchemy import (
    BigInteger, Column, String, Integer, DateTime, JSON, Float, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(String(64), unique=True, nullable=True)
    name = Column(String(128), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(32), default="user")
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_txn_id = Column(String(128), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())
    merchant_id = Column(String(128), nullable=True)
    device_id = Column(String(128), nullable=True)
    location = Column(String(128), nullable=True)
    payload = Column(JSON, nullable=True)  # raw input
    status = Column(String(16), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FraudResult(Base):
    __tablename__ = "fraudresults"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"), nullable=False)
    verdict = Column(String(16), nullable=False)  # 'legit' or 'fraud'
    fraud_score = Column(Float, nullable=False)    # normalized probability (0-1)
    reason_codes = Column(JSON, nullable=True)     # list of reasons/explanations
    decided_by = Column(String(64), nullable=False) # e.g., 'consensus'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChainBlock(Base):
    __tablename__ = "chain_blocks"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    block_index = Column(BigInteger, unique=True, nullable=False)
    prev_block_hash = Column(String(128), nullable=False)
    block_hash = Column(String(128), nullable=False)
    merkle_root = Column(String(128), nullable=True)
    entries_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChainEntry(Base):
    __tablename__ = "chain_entries"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    block_index = Column(BigInteger, nullable=False)
    entry_index = Column(Integer, nullable=False)
    tx_reference = Column(String(128), nullable=False)
    entry_payload = Column(JSON, nullable=False)
    entry_hash = Column(String(128), nullable=False)
    hmac_chain = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"), nullable=False)
    recs = Column(JSON, nullable=False)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
