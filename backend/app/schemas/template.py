# app/schemas/template.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    is_active: bool = True

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class TemplateInDBBase(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Template(TemplateInDBBase):
    pass

class TemplateResponse(TemplateInDBBase):
    pass

class TemplateList(BaseModel):
    templates: list[TemplateResponse]
    total: int