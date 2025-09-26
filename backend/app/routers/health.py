from fastapi import APIRouter
from sqlalchemy import text
from app.db.database import engine

router = APIRouter()

@router.get("/health", tags=["system"])
async def health():
    # Verify DB connectivity and a trivial query for readiness
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception as exc:
        return {"status": "degraded", "db": f"down: {type(exc).__name__}"}
