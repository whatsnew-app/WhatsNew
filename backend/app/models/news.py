from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    summary = Column(Text)
    source_urls = Column(ARRAY(String), nullable=False)
    image_url = Column(String)
    
    # Metadata
    ai_metadata = Column(JSON)  # Stores LLM config used, tokens, etc.
    prompt_id = Column(PGUUID, ForeignKey("prompts.id"), nullable=False)
    published_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompt = relationship("Prompt", back_populates="news_articles")

class NewsImage(Base):
    __tablename__ = "news_images"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    news_article_id = Column(PGUUID, ForeignKey("news_articles.id"), nullable=False)
    image_prompt = Column(Text, nullable=False)
    provider = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    ai_metadata = Column(JSON)  # Stores image generation details
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)