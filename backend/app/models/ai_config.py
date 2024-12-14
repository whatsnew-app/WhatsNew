from uuid import UUID, uuid4
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from enum import Enum
from app.core.database import Base

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

class ImageProvider(str, Enum):
    DALLE = "dalle"
    STABLE_DIFFUSION = "stable_diffusion"
    MIDJOURNEY = "midjourney"
    CUSTOM = "custom"

class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    provider = Column(SQLEnum(LLMProvider), nullable=False)
    api_key = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    endpoint_url = Column(String)
    parameters = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_by = Column(PGUUID, nullable=False)
    updated_by = Column(PGUUID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImageConfig(Base):
    __tablename__ = "image_configs"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    provider = Column(SQLEnum(ImageProvider), nullable=False)
    api_key = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    endpoint_url = Column(String)
    parameters = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_by = Column(PGUUID, nullable=False)
    updated_by = Column(PGUUID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)