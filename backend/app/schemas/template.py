# app/schemas/template.py

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_content: str
    is_active: bool = True

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_content: Optional[str] = None
    is_active: Optional[bool] = None

class TemplateInDBBase(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Template(TemplateInDBBase):
    """Schema for template responses."""
    pass

class TemplateResponse(TemplateInDBBase):
    """Schema for template responses with additional metadata."""
    pass

class TemplateList(BaseModel):
    """Schema for paginated template list."""
    items: List[TemplateResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)