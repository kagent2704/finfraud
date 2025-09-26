# backend/app/ml/train_models.py
import pandas as pd
import joblib
import os
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import numpy as np

# ==============================
# Parse arguments
# ==============================
parser = argparse.ArgumentParser()
parser.add_argument("--fast", action="store_true", help="Use small subset (20k rows) for quick testing")
args = parser.parse_args()

# ==============================
# Dataset paths
# ==============================
COMBINED_PATH = "backend/app/ml/fraud_data_combined.csv"
SYNTHETIC_PATH = "backend/app/ml/fraud_data.csv"

if os.path.exists(COMBINED_PATH):
    DATA_PATH = COMBINED_PATH
    print(f"📂 Using combined dataset: {COMBINED_PATH}")
elif os.path.exists(SYNTHETIC_PATH):
    DATA_PATH = SYNTHETIC_PATH
    print(f"📂 Using synthetic dataset: {SYNTHETIC_PATH}")
else:
    raise FileNotFoundError("❌ No dataset found! Run merge_datasets.py or generate_data.py first.")

df = pd.read_csv(DATA_PATH)

# ==============================
# Sampling (to fit laptop specs)
# ==============================
MAX_ROWS_FAST = 20_000   # for quick tests
MAX_ROWS_FULL = 200_000  # balanced run

MAX_ROWS = MAX_ROWS_FAST if args.fast else MAX_ROWS_FULL

if len(df) > MAX_ROWS:
    df = df.sample(n=MAX_ROWS, random_state=42)
    print(f"⚡ Sampled {MAX_ROWS} rows for training (from {len(df)} total)")

print(f"✅ Final dataset shape: {df.shape}")

# ==============================
# Preprocess
# ==============================
X = df.drop("is_fraud", axis=1)
y = df["is_fraud"]

# encode categoricals
X = pd.get_dummies(X)

# train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# balance with SMOTE
sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

# ==============================
# Train RandomForest
# ==============================
rf = Pipeline([
    ("scaler", StandardScaler(with_mean=False)),
    ("clf", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ))
])
rf.fit(X_train_res, y_train_res)

# ==============================
# Train XGBoost
# ==============================
xgb = Pipeline([
    ("scaler", StandardScaler(with_mean=False)),
    ("clf", XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42
    ))
])
xgb.fit(X_train_res, y_train_res)

# ==============================
# Save models
# ==============================
MODEL_DIR = "backend/app/ml"
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(rf, f"{MODEL_DIR}/rf_model.joblib")
joblib.dump(xgb, f"{MODEL_DIR}/xgb_model.joblib")

print("✅ Models trained and saved to rf_model.joblib and xgb_model.joblib")
