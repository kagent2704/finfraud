import pathlib
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[3] / "database" / "schema.sql"

async def init_schema(engine: AsyncEngine):
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    async with engine.begin() as conn:
        # Split on semicolons cautiously; MySQL driver can run multi statements with text()
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            await conn.execute(text(stmt))
