# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

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

# Configure OAuth2 with the full path
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="OAuth2PasswordBearer"
)

# Global task scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    async for db in get_db():
        scheduler = TaskScheduler(db)
        break
    logger.info("Task scheduler initialized")
    yield
    if scheduler:
        scheduler.stop()
        logger.info("Task scheduler stopped")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        routes=app.routes,
    )

    # Update the security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{settings.API_V1_STR}/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    # Add security globally
    openapi_schema["security"] = [
        {
            "OAuth2PasswordBearer": []
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root router for version check
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "api_v1_url": settings.API_V1_STR,
        "docs_url": f"{settings.API_V1_STR}/docs"
    }

# Include API router with prefix
app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.1", port=8000)