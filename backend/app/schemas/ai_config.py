from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

class ImageProvider(str, Enum):
    DALLE = "dalle"
    STABLE_DIFFUSION = "stable_diffusion"
    MIDJOURNEY = "midjourney"
    CUSTOM = "custom"

class ConfigBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_key: str
    model_name: str
    endpoint_url: Optional[str] = None
    parameters: Dict = {}
    is_active: bool = True
    is_default: bool = False

class LLMConfigCreate(ConfigBase):
    provider: LLMProvider

class ImageConfigCreate(ConfigBase):
    provider: ImageProvider

class ConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    parameters: Optional[Dict] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class ConfigInDBBase(ConfigBase):
    id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LLMConfig(ConfigInDBBase):
    provider: LLMProvider

class ImageConfig(ConfigInDBBase):
    provider: ImageProvider