# app/models/prompt.py

from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import List

from app.core.database import Base

class PromptType(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"

class DisplayStyle(str, enum.Enum):
    CARD = "card"
    RECTANGLE = "rectangle"
    HIGHLIGHT = "highlight"

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(SQLEnum(PromptType), nullable=False)
    generate_image = Column(Boolean, default=False)
    display_style = Column(SQLEnum(DisplayStyle), nullable=False)
    
    # Store RSS feed URLs
    news_sources = Column(ARRAY(String), nullable=False)
    
    # Configuration
    template_id = Column(PGUUID, ForeignKey("prompt_templates.id"), nullable=False)
    user_id = Column(PGUUID, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="prompts")
    
    # Tracking
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("PromptTemplate", back_populates="prompts")
    news_articles = relationship("NewsArticle", back_populates="prompt")

    def validate_news_sources(self, sources: List[str]) -> bool:
        """Validate news source URLs."""
        if not sources:
            return False
            
        for source in sources:
            if not source.startswith(('http://', 'https://')):
                return False
                
        return True

    def update_news_sources(self, sources: List[str]) -> None:
        """Update news sources after validation."""
        if self.validate_news_sources(sources):
            self.news_sources = sources
        else:
            raise ValueError("Invalid news source URLs provided")