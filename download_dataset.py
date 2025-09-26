import os
import kaggle

# Where to save datasets
DATA_DIR = "backend/app/ml/data"
os.makedirs(DATA_DIR, exist_ok=True)

# List of Kaggle datasets (dataset-slug format)
DATASETS = {
    "creditcard": "mlg-ulb/creditcardfraud",   # European credit card fraud dataset
    "paysim": "ealaxi/paysim1"               # PaySim mobile money simulator dataset
}

def download_all():
    for name, slug in DATASETS.items():
        print(f"📥 Downloading {name} dataset from {slug} ...")
        try:
            kaggle.api.dataset_download_files(slug, path=DATA_DIR, unzip=True)
            print(f"✅ {name} downloaded to {DATA_DIR}")
        except Exception as e:
            print(f"❌ Failed to download {name}: {e}")

if __name__ == "__main__":
    download_all()
