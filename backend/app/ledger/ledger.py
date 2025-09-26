# backend/app/ledger/ledger.py
import hashlib
import hmac
import json
import time
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings  # for hmac key

def stable_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_hmac(prev_hmac: str, payload: dict) -> str:
    """
    Compute chained HMAC: HMAC(secret, prev_hmac || payload_json)
    """
    key = settings.ledger_hmac_key.encode()
    data = (prev_hmac or "").encode() + stable_json(payload).encode()
    return hmac.new(key, data, hashlib.sha256).hexdigest()

async def get_last_block(db: AsyncSession):
    q = text("SELECT block_index, block_hash FROM chain_blocks ORDER BY block_index DESC LIMIT 1")
    res = await db.execute(q)
    row = res.first()
    if not row:
        return -1, "0"*64
    return int(row[0]), row[1]

async def get_last_hmac(db: AsyncSession) -> str:
    r = await db.execute(text("SELECT hmac_chain FROM chain_entries ORDER BY id DESC LIMIT 1"))
    row = r.first()
    if not row:
        return "0"*64
    return row[0]

async def append_block(db: AsyncSession, entries: List[Dict[str,Any]]):
    """
    entries: list of dicts with tx_reference and payload (minimal, non-PII)
    """
    last_index, prev_hash = await get_last_block(db)
    block_index = last_index + 1

    entry_hashes = []
    for e in entries:
        h = sha256_hex(stable_json(e["payload"]).encode("utf-8"))
        entry_hashes.append(h)

    # simple merkle-like root = sha256(concat hashes)
    merkle_root = sha256_hex("".join(entry_hashes).encode("utf-8")) if entry_hashes else sha256_hex(b"")

    header = stable_json({
        "block_index": block_index,
        "prev_block_hash": prev_hash,
        "merkle_root": merkle_root,
        "entries_count": len(entries),
        "timestamp": int(time.time())
    }).encode("utf-8")
    block_hash = sha256_hex(header)

    # persist block
    await db.execute(text("""
        INSERT INTO chain_blocks (block_index, prev_block_hash, block_hash, merkle_root, entries_count)
        VALUES (:block_index, :prev, :block_hash, :merkle_root, :entries_count)
    """), {
        "block_index": block_index,
        "prev": prev_hash,
        "block_hash": block_hash,
        "merkle_root": merkle_root,
        "entries_count": len(entries)
    })

    # compute HMAC chain
    prev_hmac = await get_last_hmac(db)
    key = settings.ledger_hmac_key.encode("utf-8") if settings.ledger_hmac_key else b"secret-default-key"

    for idx, (entry, ehash) in enumerate(zip(entries, entry_hashes), start=1):
        # compute running hmac: HMAC(k, entry_hash || prev_hmac)
        hm = hmac.new(key, (ehash + prev_hmac).encode("utf-8"), hashlib.sha256).hexdigest()
        await db.execute(text("""
            INSERT INTO chain_entries (block_index, entry_index, tx_reference, entry_payload, entry_hash, hmac_chain)
            VALUES (:block_index, :entry_index, :tx_reference, :entry_payload, :entry_hash, :hmac_chain)
        """), {
            "block_index": block_index,
            "entry_index": idx,
            "tx_reference": str(entry.get("tx_reference")),
            "entry_payload": stable_json(entry["payload"]),
            "entry_hash": ehash,
            "hmac_chain": hm
        })
        prev_hmac = hm

    await db.commit()
    return {"block_index": block_index, "block_hash": block_hash, "merkle_root": merkle_root}
