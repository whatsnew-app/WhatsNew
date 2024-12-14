# app/schemas/prompt.py

from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from enum import Enum
from app.models.prompt import PromptType
from app.schemas.template import Template

class DisplayStyle(str, Enum):
    CARD = "card"
    RECTANGLE = "rectangle"
    HIGHLIGHT = "highlight"

class PromptBase(BaseModel):
    name: str
    content: str
    type: PromptType
    generate_image: bool = False
    display_style: DisplayStyle
    news_sources: List[str]
    template_id: UUID

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    type: Optional[PromptType] = None
    generate_image: Optional[bool] = None
    display_style: Optional[DisplayStyle] = None
    news_sources: Optional[List[str]] = None
    template_id: Optional[UUID] = None

class PromptInDBBase(PromptBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Prompt(PromptInDBBase):
    """Schema for prompt responses."""
    template: Optional[Template] = None

class PromptResponse(PromptInDBBase):
    """Schema for detailed prompt responses."""
    template: Optional[Template] = None
    last_run_at: Optional[datetime] = None
    news_count: Optional[int] = None

class PromptList(BaseModel):
    """Schema for paginated prompt list."""
    items: List[PromptResponse]
    total: int
    skip: int
    limit: int

class PromptInDB(PromptInDBBase):
    """Schema for prompt in database."""
    pass