# app/models/stats.py

from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class SystemStats(Base):
    __tablename__ = "system_stats"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # User statistics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    active_sessions = Column(Integer, default=0)
    
    # Content statistics
    total_prompts = Column(Integer, default=0)
    active_prompts = Column(Integer, default=0)
    total_news_articles = Column(Integer, default=0)
    articles_last_24h = Column(Integer, default=0)
    
    # Performance metrics
    avg_news_generation_time = Column(Float, nullable=True)
    avg_image_generation_time = Column(Float, nullable=True)
    system_load = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    
    # Task statistics
    pending_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    
    # Additional metrics
    api_requests_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    detailed_metrics = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<SystemStats {self.timestamp.isoformat()}>"

class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    date = Column(DateTime, index=True, nullable=False)
    
    # Daily content metrics
    new_users = Column(Integer, default=0)
    new_prompts = Column(Integer, default=0)
    articles_generated = Column(Integer, default=0)
    images_generated = Column(Integer, default=0)
    
    # Usage metrics
    total_api_requests = Column(Integer, default=0)
    unique_active_users = Column(Integer, default=0)
    peak_concurrent_users = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    system_uptime = Column(Float, nullable=True)
    
    # Resource usage
    cpu_usage_avg = Column(Float, nullable=True)
    memory_usage_avg = Column(Float, nullable=True)
    disk_usage_avg = Column(Float, nullable=True)
    
    # Cost metrics (if applicable)
    llm_api_cost = Column(Float, default=0.0)
    image_api_cost = Column(Float, default=0.0)
    
    # Additional data
    metrics_breakdown = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<DailyStats {self.date.date().isoformat()}>"

    @classmethod
    async def get_or_create(cls, db, date):
        """Get existing stats for date or create new entry."""
        stats = await db.query(cls).filter(cls.date == date).first()
        if not stats:
            stats = cls(date=date)
            db.add(stats)
            await db.commit()
        return stats

    def to_dict(self):
        """Convert stats to dictionary for serialization."""
        return {
            "id": str(self.id),
            "date": self.date.date().isoformat(),
            "new_users": self.new_users,
            "new_prompts": self.new_prompts,
            "articles_generated": self.articles_generated,
            "images_generated": self.images_generated,
            "total_api_requests": self.total_api_requests,
            "unique_active_users": self.unique_active_users,
            "peak_concurrent_users": self.peak_concurrent_users,
            "avg_response_time": self.avg_response_time,
            "error_rate": self.error_rate,
            "system_uptime": self.system_uptime,
            "resource_usage": {
                "cpu": self.cpu_usage_avg,
                "memory": self.memory_usage_avg,
                "disk": self.disk_usage_avg
            },
            "api_costs": {
                "llm": self.llm_api_cost,
                "image": self.image_api_cost
            },
            "metrics_breakdown": self.metrics_breakdown
        }