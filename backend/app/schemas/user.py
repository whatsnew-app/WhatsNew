# app/schemas/user.py

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class SuperUserCreate(UserCreate):
    """Schema for creating superusers."""
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    """Schema for user responses."""
    pass

class UserList(BaseModel):
    """Schema for paginated user list."""
    users: List[User]
    total: int
    skip: int
    limit: int

class UserInDB(UserInDBBase):
    """Schema for user in database."""
    password: str