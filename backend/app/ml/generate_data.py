import pandas as pd
import numpy as np

def generate_synthetic_fraud_data(n_samples=5000, fraud_ratio=0.1, random_state=42):
    np.random.seed(random_state)

    # number of fraud vs legit
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # Legit transactions
    legit = pd.DataFrame({
        "amount": np.random.gamma(2.0, 2000, n_legit),   # mostly smaller amounts
        "device_risk_score": np.random.beta(2, 5, n_legit),  # skewed low
        "location": np.random.choice(["Pune", "Mumbai", "Delhi", "Bangalore"], n_legit),
        "is_fraud": 0
    })

    # Fraud transactions
    fraud = pd.DataFrame({
        "amount": np.random.gamma(4.0, 8000, n_fraud),   # higher amounts
        "device_risk_score": np.random.beta(5, 2, n_fraud),  # skewed high
        "location": np.random.choice(["Remote-VPN", "Nigeria", "Russia"], n_fraud),
        "is_fraud": 1
    })

    df = pd.concat([legit, fraud], ignore_index=True)
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)  # shuffle

    return df

if __name__ == "__main__":
    df = generate_synthetic_fraud_data()
    df.to_csv("backend/app/ml/fraud_data.csv", index=False)
    print("✅ Synthetic fraud dataset saved to backend/app/ml/fraud_data.csv")
