# app/models/prompt.py

from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class PromptType(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"

class DisplayStyle(str, Enum):
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
    news_sources = Column(ARRAY(String), nullable=False)
    template_id = Column(PGUUID, ForeignKey("prompt_templates.id"), nullable=False)
    user_id = Column(PGUUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="prompts")
    template = relationship("PromptTemplate")
    news_articles = relationship("NewsArticle", back_populates="prompt")