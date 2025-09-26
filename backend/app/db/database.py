from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# ✅ Add declarative base
Base = declarative_base()

# Create engine once at import time
engine = create_async_engine(
    settings.async_mysql_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

# Session factory (SQLAlchemy 2.0 style)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)

# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # session closes automatically

# ✅ Alias for legacy imports
get_session = get_db
