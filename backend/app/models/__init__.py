from app.core.database import Base

from app.models.user import User
from app.models.prompt import Prompt
from app.models.prompt_template import PromptTemplate
from app.models.news import NewsArticle, NewsImage
from app.models.ai_config import LLMConfig, ImageConfig

# This makes Base and all models available when importing from app.models
__all__ = [
    "Base",
    "User",
    "Prompt",
    "PromptTemplate",
    "NewsArticle",
    "NewsImage",
    "LLMConfig",
    "ImageConfig"
]