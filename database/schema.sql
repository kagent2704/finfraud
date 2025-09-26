-- Ensure deterministic charset/collation
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Users
CREATE TABLE IF NOT EXISTS users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  external_id VARCHAR(64) UNIQUE,
  name VARCHAR(128),
  email VARCHAR(255) UNIQUE,
  hashed_password VARCHAR(255) DEFAULT NULL,
  role ENUM('admin','analyst','user') DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  risk_score DOUBLE DEFAULT 0.0,             -- ✅ cumulative user risk score
  KEY idx_users_email (email)
) ENGINE=InnoDB;

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  external_txn_id VARCHAR(255),                -- external reference
  user_id BIGINT,
  amount DECIMAL(14,2) NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'INR',
  occurred_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  location VARCHAR(128),
  device_id VARCHAR(128),
  merchant_id VARCHAR(128),
  status ENUM('pending','legit','fraud') DEFAULT 'pending',
  payload JSON,                                -- raw request
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  KEY idx_tx_user_time (user_id, occurred_at),
  KEY idx_tx_merchant_time (merchant_id, occurred_at)
) ENGINE=InnoDB;

-- Fraud results (per transaction decision)
CREATE TABLE IF NOT EXISTS fraudresults (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  verdict ENUM('legit','fraud') NOT NULL,
  fraud_score DOUBLE NOT NULL,
  consensus_score DOUBLE DEFAULT 0.0,         -- ✅ added for multi-agent consensus
  reason_codes JSON NULL,
  decided_by VARCHAR(64) NOT NULL,            -- e.g., 'xgboost', 'rf', 'rules', 'consensus'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id),
  KEY idx_fraudresults_tx (transaction_id),
  KEY idx_fraudresults_verdict_time (verdict, created_at)
) ENGINE=InnoDB;

-- Recommendations (linked to transactions)
CREATE TABLE IF NOT EXISTS recommendations (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  recs JSON NOT NULL,             -- array of recommendation objects
  confidence DOUBLE DEFAULT 0.0,  -- highest confidence among recs
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id),
  KEY idx_recs_tx (transaction_id)
) ENGINE=InnoDB;

-- Ledger blocks (Merkle, chaining)
CREATE TABLE IF NOT EXISTS chain_blocks (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  block_index BIGINT NOT NULL UNIQUE,
  prev_block_hash CHAR(64) NOT NULL,
  merkle_root CHAR(64) NOT NULL,
  block_hash CHAR(64) NOT NULL,
  entries_count INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY idx_blocks_created (created_at)
) ENGINE=InnoDB;

-- Ledger entries (tamper-evident)
CREATE TABLE IF NOT EXISTS chain_entries (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  block_index BIGINT NOT NULL,
  entry_index INT NOT NULL,
  tx_reference VARCHAR(64) NOT NULL, -- e.g., transaction_id or composite ref
  entry_payload JSON NOT NULL,       -- minimized payload / digest metadata
  entry_hash CHAR(64) NOT NULL,      -- SHA-256 of payload
  hmac_chain CHAR(64) NOT NULL,      -- HMAC(k, entry_i || hmac_{i-1})
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_block_entry (block_index, entry_index),
  FOREIGN KEY (block_index) REFERENCES chain_blocks(block_index)
) ENGINE=InnoDB;
