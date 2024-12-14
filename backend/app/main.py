# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.api.v1.router import api_router
from app.core.config import settings
from app.tasks.scheduler import TaskScheduler
from app.core.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global task scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler
    
    # Initialize task scheduler
    async for db in get_db():
        scheduler = TaskScheduler(db)
        # Start scheduler in background task
        asyncio.create_task(scheduler.start())
        break
    
    logger.info("Task scheduler initialized and started")
    yield
    
    # Shutdown
    if scheduler:
        scheduler.stop()
        logger.info("Task scheduler stopped")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "api_v1_url": settings.API_V1_STR
    }

@app.on_event("startup")
async def startup_event():
    """Additional startup tasks."""
    logger.info("Application starting up...")
    # Additional startup tasks can be added here

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Application shutting down...")
    # Additional cleanup tasks can be added here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )