# app/schemas/stats.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    system_load: float

class UserStats(BaseModel):
    total_users: int
    active_users: int
    active_sessions: int

class ContentStats(BaseModel):
    total_prompts: int
    active_prompts: int
    total_news_articles: int
    articles_last_24h: int

class TaskStats(BaseModel):
    pending_tasks: int
    failed_tasks: int
    completed_tasks: int
    avg_completion_time: Optional[float] = None

class PerformanceMetrics(BaseModel):
    avg_news_generation_time: Optional[float] = None
    avg_image_generation_time: Optional[float] = None
    api_response_time: Optional[float] = None
    error_rate: Optional[float] = None

class SystemStatsBase(BaseModel):
    user_stats: UserStats
    content_stats: ContentStats
    task_stats: TaskStats
    performance_metrics: PerformanceMetrics
    system_metrics: SystemMetrics
    detailed_metrics: Optional[Dict[str, Any]] = None

class SystemStatsCreate(SystemStatsBase):
    pass

class SystemStatsInDBBase(SystemStatsBase):
    id: UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SystemStats(SystemStatsInDBBase):
    pass

class DailyMetrics(BaseModel):
    new_users: int
    new_prompts: int
    articles_generated: int
    images_generated: int
    total_api_requests: int
    unique_active_users: int
    peak_concurrent_users: int

class ResourceUsage(BaseModel):
    cpu_usage_avg: float
    memory_usage_avg: float
    disk_usage_avg: float

class ApiCosts(BaseModel):
    llm_api_cost: float
    image_api_cost: float

class DailyStatsBase(BaseModel):
    metrics: DailyMetrics
    resource_usage: ResourceUsage
    api_costs: ApiCosts
    avg_response_time: Optional[float] = None
    error_rate: Optional[float] = None
    system_uptime: Optional[float] = None
    metrics_breakdown: Optional[Dict[str, Any]] = None

class DailyStatsCreate(DailyStatsBase):
    date: datetime

class DailyStatsInDBBase(DailyStatsBase):
    id: UUID
    date: datetime

    model_config = ConfigDict(from_attributes=True)

class DailyStats(DailyStatsInDBBase):
    pass

class StatsSummary(BaseModel):
    start_date: datetime
    end_date: datetime
    stats: List[DailyStats]
    
class StatsResponse(BaseModel):
    current: SystemStats
    daily: Optional[StatsSummary] = None