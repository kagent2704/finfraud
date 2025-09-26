from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import engine
from app.db.init_schema import init_schema
from app.routers.health import router as health_router
from app.routers.chain import router as chain_router
from app.routers import fraud  # 👈 import the fraud router
from app.routers import auth as auth_router
from starlette.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: initialize schema (idempotent)
    await init_schema(engine)
    yield
    # On shutdown: nothing special

app = FastAPI(
    title="FinFraud API",
    version="1.0.0",
    description="Fraud detection backend with verifiable audit ledger",
    lifespan=lifespan,
)

# Allow dev frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(chain_router)
app.include_router(fraud.router)  # 👈 register fraud endpoints
app.include_router(auth_router.router)  # register auth router