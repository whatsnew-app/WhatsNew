# app/models/base.py

from app.core.database import Base
from app.models.user import User
from app.models.task import Task
from app.models.prompt import Prompt
from app.models.news import NewsArticle
from app.models.prompt_template import PromptTemplate
from app.models.ai_config import LLMConfig, ImageConfig

# Import all models here to ensure they're registered
__all__ = [
    'User',
    'Task',
    'Prompt',
    'NewsArticle',
    'PromptTemplate',
    'LLMConfig',
    'ImageConfig'
]