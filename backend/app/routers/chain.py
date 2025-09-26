from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.database import get_session

router = APIRouter(prefix="/chain", tags=["chain"])

@router.get("/latest")
async def chain_latest(db=Depends(get_session)):
    r = await db.execute(
        text(
            """
            SELECT block_index, block_hash, merkle_root, entries_count, created_at
            FROM chain_blocks
            ORDER BY block_index DESC
            LIMIT 1
            """
        )
    )
    row = r.first()
    if not row:
        return {}
    # row is a Row; map to keys
    return {
        "block_index": row[0],
        "block_hash": row[1],
        "merkle_root": row[2],
        "entries_count": row[3],
        "created_at": str(row[4])
    }