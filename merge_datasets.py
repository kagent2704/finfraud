import os
import pandas as pd
import numpy as np

DATA_DIR = "backend/app/ml/data"
OUT_FILE = "backend/app/ml/fraud_data_combined.csv"

def load_synthetic():
    path = "backend/app/ml/fraud_data.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"✅ Loaded synthetic dataset: {df.shape}")
        return df
    return pd.DataFrame()

def load_creditcard():
    path = os.path.join(DATA_DIR, "creditcard.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        # rename to common schema
        df = df.rename(columns={"Amount": "amount", "Class": "is_fraud"})
        df["device_risk_score"] = np.random.rand(len(df))  # synthetic risk score
        df["location"] = "EU"  # anonymized dataset, no location info
        print(f"✅ Loaded creditcard dataset: {df.shape}")
        return df[["amount", "device_risk_score", "location", "is_fraud"]]
    return pd.DataFrame()

def load_paysim():
    path = os.path.join(DATA_DIR, "PS_20174392719_1491204439457_log.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df.rename(columns={"amount": "amount", "isFraud": "is_fraud"})
        df["device_risk_score"] = np.random.rand(len(df))
        df["location"] = df["type"].map(lambda x: "mobile" if x in ["CASH_OUT","TRANSFER"] else "other")
        print(f"✅ Loaded paysim dataset: {df.shape}")
        return df[["amount", "device_risk_score", "location", "is_fraud"]]
    return pd.DataFrame()

def load_ieee():
    path = os.path.join(DATA_DIR, "train_transaction.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=50000)  # limit for memory
        df = df.rename(columns={"TransactionAmt": "amount", "isFraud": "is_fraud"})
        df["device_risk_score"] = np.random.rand(len(df))
        df["location"] = "unknown"
        print(f"✅ Loaded ieee dataset: {df.shape}")
        return df[["amount", "device_risk_score", "location", "is_fraud"]]
    return pd.DataFrame()

def main():
    dfs = []
    for loader in [load_synthetic, load_creditcard, load_paysim, load_ieee]:
        dfs.append(loader())
    combined = pd.concat(dfs, ignore_index=True)
    print(f"📊 Combined dataset shape: {combined.shape}")
    combined.to_csv(OUT_FILE, index=False)
    print(f"✅ Saved merged dataset to {OUT_FILE}")

if __name__ == "__main__":
    main()
