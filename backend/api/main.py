from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from db.connection import get_pool, close_pool
from api.routes import auth, upload, sessions, ask


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting up...")
    try:
        await get_pool()
        logging.info("Database pool initialized")
    except Exception as e:
        logging.warning(f"Database not available: {e}")
    
    yield
    
    # Shutdown
    logging.info("Shutting down...")
    try:
        await close_pool()
    except Exception as e:
        logging.warning(f"Error closing database pool: {e}")


app = FastAPI(
    title="DataLens AI API",
    description="Conversational BI for non-technical teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(sessions.router)
app.include_router(ask.router)


@app.get("/")
def root():
    return {"message": "DataLens AI API is running!"}


@app.get("/health")
async def health():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }