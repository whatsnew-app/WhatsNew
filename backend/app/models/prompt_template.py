from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    template_content = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompts = relationship("Prompt", back_populates="template")