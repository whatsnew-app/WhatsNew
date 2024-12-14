# app/core/config.py

from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    PROJECT_NAME: str = "News Summarizer API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for news summarization with AI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",     # React frontend
        "http://localhost:8000",     # API documentation
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Task Scheduler
    TASK_CHECK_INTERVAL: int = 60  # seconds
    MAX_TASK_RETRIES: int = 3
    TASK_TIMEOUT: int = 300  # seconds
    
    # News Generation
    NEWS_GENERATION_INTERVAL: int = 3600  # 1 hour in seconds
    NEWS_GENERATION_CRON: str = "0 * * * *"  # Every hour
    MAX_RSS_ITEMS_PER_SOURCE: int = 10
    CONTENT_MAX_LENGTH: int = 10000
    
    # System Monitoring
    STATS_COLLECTION_INTERVAL: int = 300  # 5 minutes in seconds
    MONITORING_RETENTION_DAYS: int = 30
    ALERT_THRESHOLDS: Dict[str, float] = {
        "cpu_usage": 80.0,        # percentage
        "memory_usage": 80.0,     # percentage
        "disk_usage": 80.0,       # percentage
        "error_rate": 5.0         # percentage
    }
    
    # Default superuser
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    
    # LLM Defaults
    DEFAULT_LLM_TIMEOUT: int = 60  # seconds
    DEFAULT_LLM_MAX_TOKENS: int = 2000
    DEFAULT_LLM_TEMPERATURE: float = 0.7
    
    # Image Generation
    DEFAULT_IMAGE_SIZE: str = "1024x1024"
    DEFAULT_IMAGE_QUALITY: str = "standard"
    IMAGE_STORAGE_PATH: str = "media/images"
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour in seconds
    CACHE_PREFIX: str = "news_summarizer:"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    MAX_REQUESTS_PER_WINDOW: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def task_check_interval_td(self) -> timedelta:
        """Get task check interval as timedelta."""
        return timedelta(seconds=self.TASK_CHECK_INTERVAL)
    
    @property
    def news_generation_interval_td(self) -> timedelta:
        """Get news generation interval as timedelta."""
        return timedelta(seconds=self.NEWS_GENERATION_INTERVAL)

settings = Settings()