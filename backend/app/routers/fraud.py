# backend/app/routers/fraud.py
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.ml.predictor import predict_models
from app.ledger.ledger import append_block
from app.db.database import get_session

router = APIRouter(prefix="/api", tags=["fraud"])


# ------------------------------
# Transaction Prediction Input
# ------------------------------
class TxnIn(BaseModel):
    external_txn_id: str | None
    user_external_id: str | None
    amount: float
    currency: str | None = "INR"
    merchant_id: str | None = None
    device_id: str | None = None
    location: str | None = None
    device_risk_score: float | None = 0.0


# ------------------------------
# Fraud Prediction Endpoint
# ------------------------------
@router.post("/predict")
async def predict(txn: TxnIn, db=Depends(get_session)):
    payload = txn.dict()

    # -----------------------------------
    # 1) Normalize + One-hot location
    # -----------------------------------
    # 1) Debug raw payload (predictor.py will handle encoding)
    print("🟢 Raw payload received in /predict:", payload)
    # -----------------------------------
    # 2) Persist transaction as before
    # -----------------------------------
    await db.execute(text("""
        INSERT INTO transactions (
            external_txn_id, amount, currency, merchant_id, device_id, location, payload
        )
        VALUES (:external_txn_id, :amount, :currency, :merchant_id, :device_id, :location, :payload)
    """), {
        "external_txn_id": payload.get("external_txn_id"),
        "amount": payload["amount"],
        "currency": payload.get("currency"),
        "merchant_id": payload.get("merchant_id"),
        "device_id": payload.get("device_id"),
        "location": payload.get("location"),
        "payload": json.dumps(payload)
    })
    await db.commit()

    txn_row = await db.execute(text("SELECT LAST_INSERT_ID()"))
    txn_id = txn_row.scalar() or None

    # -----------------------------------
    # 3) Run ML models
    # -----------------------------------
    consensus, reason_codes = predict_models(payload)
    verdict = consensus["consensus_verdict"]
    consensus_score = consensus["consensus_score"]
    fraud_score = max(a["score"] for a in consensus["agents"])

    # 3) Persist fraud result
    await db.execute(text("""
        INSERT INTO fraudresults (
            transaction_id, verdict, fraud_score, consensus_score, reason_codes, decided_by
        )
        VALUES (:transaction_id, :verdict, :fraud_score, :consensus_score, :reason_codes, :decided_by)
    """), {
        "transaction_id": txn_id,
        "verdict": verdict,
        "fraud_score": fraud_score,
        "consensus_score": consensus_score,
        "reason_codes": json.dumps(reason_codes),
        "decided_by": "consensus"
    })

    # 4) Update user risk score (cumulative with decay)
    new_risk = None
    if payload.get("user_external_id"):
        u = await db.execute(
            text("SELECT id, risk_score FROM users WHERE external_id=:eid"),
            {"eid": payload["user_external_id"]}
        )
        row = u.first()
        if row:
            uid, current = row
            new_risk = float((current or 0.0) * 0.8 + consensus_score * 0.2)
            await db.execute(
                text("UPDATE users SET risk_score=:rs WHERE id=:id"),
                {"rs": new_risk, "id": uid}
            )
        else:
            new_risk = consensus_score
            await db.execute(
                text("INSERT INTO users (external_id, risk_score) VALUES (:eid, :rs)"),
                {"eid": payload["user_external_id"], "rs": new_risk}
            )

    # 5) Append to blockchain
    entries = [{
        "tx_reference": txn_id,
        "payload": {
            "txn_id": txn_id,
            "verdict": verdict,
            "fraud_score": fraud_score,
            "consensus_score": consensus_score,
            "user_external_id": payload.get("user_external_id"),
            "risk_score": new_risk
        }
    }]
    block_meta = await append_block(db, entries)

    # 6) Update transaction status
    await db.execute(
        text("UPDATE transactions SET status=:status WHERE id=:id"),
        {"status": verdict, "id": txn_id}
    )

    # 7) Generate recommendations
    from app.recommendation.engine import generate_recommendations
    recs = generate_recommendations(verdict, {"agents": consensus.get("agents", [])})
    await db.execute(text("""
        INSERT INTO recommendations (transaction_id, recs, confidence)
        VALUES (:txid, :recs, :conf)
    """), {
        "txid": txn_id,
        "recs": json.dumps(recs),
        "conf": max((r["confidence"] for r in recs), default=0.0)
    })
    await db.commit()

    return {
        "transaction_id": txn_id,
        "verdict": verdict,
        "fraud_score": fraud_score,
        "consensus_score": consensus_score,
        "risk_score": new_risk,
        "block": block_meta,
        "recs": recs
    }


# ------------------------------
# Fetch Recommendations by Transaction
# ------------------------------
@router.get("/recommendations/{txn_id}")
async def get_recommendations(txn_id: int, db=Depends(get_session)):
    res = await db.execute(
        text("SELECT recs, confidence, created_at FROM recommendations WHERE transaction_id=:txid"),
        {"txid": txn_id}
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No recommendations found for txn_id={txn_id}")

    recs, confidence, created_at = row
    return {
        "transaction_id": txn_id,
        "recommendations": json.loads(recs),
        "confidence": confidence,
        "created_at": str(created_at),
    }


# ------------------------------
# Fetch Transaction with Fraud Result + Recs
# ------------------------------
@router.get("/transactions/{txn_id}")
async def get_transaction(txn_id: int, db=Depends(get_session)):
    res = await db.execute(text("""
        SELECT t.id, t.external_txn_id, t.amount, t.currency, t.status, t.created_at,
               f.verdict, f.fraud_score, f.consensus_score, f.reason_codes,
               r.recs, r.confidence
        FROM transactions t
        LEFT JOIN fraudresults f ON t.id = f.transaction_id
        LEFT JOIN recommendations r ON t.id = r.transaction_id
        WHERE t.id = :txid
    """), {"txid": txn_id})
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No transaction found for txn_id={txn_id}")

    (
        id, external_txn_id, amount, currency, status, created_at,
        verdict, fraud_score, consensus_score, reason_codes,
        recs, confidence
    ) = row

    return {
        "transaction_id": id,
        "external_txn_id": external_txn_id,
        "amount": float(amount),
        "currency": currency,
        "status": status,
        "created_at": str(created_at),
        "verdict": verdict,
        "fraud_score": fraud_score,
        "consensus_score": consensus_score,
        "reason_codes": json.loads(reason_codes) if reason_codes else None,
        "recommendations": json.loads(recs) if recs else None,
        "confidence": confidence,
    }


# ------------------------------
# Fetch User Risk Profile
# ------------------------------
@router.get("/users/{external_id}/risk")
async def get_user_risk(external_id: str, db=Depends(get_session)):
    res = await db.execute(
        text("SELECT external_id, risk_score, created_at FROM users WHERE external_id=:eid"),
        {"eid": external_id}
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "external_id": row[0],
        "risk_score": row[1],
        "created_at": str(row[2]),
    }
