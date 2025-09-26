import uvicorn
import pathlib
import os
import pymysql

if __name__ == "__main__":
    cwd = pathlib.Path().resolve()
    print(f"🚀 Starting FastAPI with working dir: {cwd}")
    print(f"📂 Python path: {os.sys.path[:3]} ...")  # show first few entries

    # ----------------------------
    # ✅ Check ML models
    # ----------------------------
    ml_dir = cwd / "app" / "ml"
    rf_model = ml_dir / "rf_model.joblib"
    xgb_model = ml_dir / "xgb_model.joblib"

    if rf_model.exists() and xgb_model.exists():
        print(f"✅ Models found: {rf_model.name}, {xgb_model.name}")
    else:
        print("⚠️ WARNING: One or both model files are missing!")
        if not rf_model.exists():
            print(f"   ❌ Missing: {rf_model}")
        if not xgb_model.exists():
            print(f"   ❌ Missing: {xgb_model}")
        print("👉 Run `python backend/app/ml/train_models.py --fast` to train and save them.")

    # ----------------------------
    # ✅ Check MySQL schema
    # ----------------------------
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=3307,
            user="user",
            password="fraudpass",
            database="frauddb",
            connect_timeout=5
        )
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = {row[0] for row in cur.fetchall()}
            required = {"users", "transactions", "fraudresults", "recommendations", "chain_blocks", "chain_entries"}

            missing = required - tables
            if not missing:
                print(f"✅ All required DB tables exist: {', '.join(required)}")
            else:
                print("⚠️ WARNING: Missing tables in MySQL schema!")
                for t in missing:
                    print(f"   ❌ {t}")
                print("👉 Run `Get-Content .\\database\\schema.sql | docker exec -i finfraud-mysql-1 mysql -uuser -pfraudpass frauddb`")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("👉 Make sure MySQL container is running: `docker compose up -d mysql`")

    # ----------------------------
    # 🚀 Start FastAPI
    # ----------------------------
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
