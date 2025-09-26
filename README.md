# FinFraud – AI-Powered FinTech Fraud Detection with Blockchain Audit
Vision
A deployable fraud detection system that uses machine learning, explainability, and blockchain-backed audit logs to provide real-time, transparent, and tamper-proof fraud detection for financial transactions.
Core MVP Features
  1. Real-time Fraud Detection
      a. Multiple ML models (e.g., XGBoost, Random Forest).
      b. Industry-grade preprocessing (imbalanced data handling, feature engineering).
      c. Outputs fraud score, verdict (fraud/legit), and reason codes for transparency.
  2. Immutable Blockchain Ledger
     a. Custom lightweight blockchain (hash chaining + Merkle + HMAC).
     b. Stores all fraud decisions immutably for audit/compliance.
     c. Multi-agent consensus (fraud verdict only committed if majority models agree).
  3. Customer Risk Profiles
     a. Each user’s cumulative fraud/risk score tracked on-chain.
     b. Historical behavior influences real-time predictions.
  4. Recommendation Engine
     a. For Customers: Safety tips, next best actions if fraud detected.
     b. For Analysts: Ranked suspicious transactions for manual review.
     c. For Product Teams: Cluster suspicious merchants/customers for insights.
  5. Frontend Dashboard
     a. React + Tailwind (or Streamlit for speed).
     b. Panels for transaction submission, fraud verdicts, recommendations, and blockchain log viewer.
  6. Deployment & Packaging
     a. Dockerized stack (FastAPI backend, MySQL DB, React frontend, blockchain service).
     b. Single docker compose up launch.
