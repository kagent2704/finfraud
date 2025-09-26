import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import pathlib

# Resolve paths relative to this file's directory
BASE_DIR = pathlib.Path(__file__).resolve().parent
RF_PATH = BASE_DIR / "rf_model.joblib"
XGB_PATH = BASE_DIR / "xgb_model.joblib"

# lazy load
_rf = None
_xgb = None

# Features used during training
FEATURES = ["amount", "device_risk_score", "location"]


def load_models():
    global _rf, _xgb
    if _rf is None:
        print(f"🔎 Loading RF model from: {RF_PATH}")
        _rf = joblib.load(RF_PATH)
    if _xgb is None:
        print(f"🔎 Loading XGB model from: {XGB_PATH}")
        _xgb = joblib.load(XGB_PATH)
    return _rf, _xgb


def get_feature_names(model) -> List[str]:
    """Extract feature names from model or pipeline."""
    if hasattr(model, "feature_names_in_"):
        return model.feature_names_in_.tolist()
    elif hasattr(model, "named_steps") and "clf" in model.named_steps:
        clf = model.named_steps["clf"]
        if hasattr(clf, "feature_names_in_"):
            return clf.feature_names_in_.tolist()
    return FEATURES  # fallback to base FEATURES


def preprocess_row(row: Dict, model_features: List[str]) -> pd.DataFrame:
    """Convert raw transaction dict into model-ready DataFrame."""
    filtered = {k: row.get(k) for k in FEATURES if k in row}
    df = pd.DataFrame([filtered])

    # One-hot encode location
    if "location" in df.columns:
        df = pd.get_dummies(df, columns=["location"])

    # Add missing cols
    for col in model_features:
        if col not in df.columns:
            df[col] = 0

    # Reorder to match training
    return df[model_features]


def predict_models(row: Dict) -> Tuple[Dict, List]:
    """
    row: single transaction dict
    returns: (consensus dict), list of per-agent reason_codes
    """
    rf, xgb = load_models()

    # Get feature names dynamically
    rf_features = get_feature_names(rf)
    xgb_features = get_feature_names(xgb)

    # --- DEBUG LOGS ---
    print("🟢 Incoming payload:", row)

    # Preprocess
    df_rf = preprocess_row(row, rf_features)
    print("🟠 RF features:", df_rf.columns.tolist())

    df_xgb = preprocess_row(row, xgb_features)
    print("🔵 XGB features:", df_xgb.columns.tolist())

    # Predict fraud probability
    rf_proba = (
        rf.predict_proba(df_rf)[:, 1][0]
        if hasattr(rf, "predict_proba")
        else float(rf.predict(df_rf)[0])
    )
    xgb_proba = (
        xgb.predict_proba(df_xgb)[:, 1][0]
        if hasattr(xgb, "predict_proba")
        else float(xgb.predict(df_xgb)[0])
    )

    rf_verdict = "fraud" if rf_proba >= 0.5 else "legit"
    xgb_verdict = "fraud" if xgb_proba >= 0.5 else "legit"

    # simple rules
    rule_reasons = []
    rule_verdict = "legit"
    amount = float(row.get("amount", 0.0))
    if amount > 50000:
        rule_verdict = "fraud"
        rule_reasons.append("high_amount")
    if row.get("device_risk_score", 0) > 0.8:
        rule_verdict = "fraud"
        rule_reasons.append("device_risk")

    agents = [
        {"name": "rf", "verdict": rf_verdict, "score": float(rf_proba)},
        {"name": "xgb", "verdict": xgb_verdict, "score": float(xgb_proba)},
        {
            "name": "rules",
            "verdict": rule_verdict,
            "score": 1.0 if rule_verdict == "fraud" else 0.0,
            "reasons": rule_reasons,
        },
    ]

    # consensus
    votes = [1 if a["verdict"] == "fraud" else 0 for a in agents]
    consensus_verdict = "fraud" if sum(votes) >= 2 else "legit"
    consensus_score = float(np.mean([a["score"] for a in agents]))

    reason_codes = {"agents": agents, "rules": rule_reasons}

    return {
        "consensus_verdict": consensus_verdict,
        "consensus_score": consensus_score,
        "agents": agents,
    }, reason_codes
