from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class PromptType(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"

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

class PromptUpdate(PromptBase):
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
    pass

class PromptTemplate(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    template_content: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)