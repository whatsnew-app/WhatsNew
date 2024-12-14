# app/api/v1/endpoints/admin.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_superuser
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserList,
    SuperUserCreate
)

router = APIRouter()

@router.get("/users", response_model=UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> UserList:
    """List all users (superuser only)."""
    # Get total count
    total = await db.scalar(select(func.count()).select_from(User))
    
    # Get users with pagination
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserList(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/superuser/create", response_model=UserSchema)
async def create_superuser(
    user_in: SuperUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> User:
    """Create a new superuser (superuser only)."""
    # Check if email already exists
    existing_user = await db.scalar(
        select(User).where(User.email == user_in.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new superuser
    user = User(
        email=user_in.email,
        password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=True,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> User:
    """Update user details (superuser only)."""
    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check email uniqueness if being updated
    if user_in.email and user_in.email != user.email:
        existing_user = await db.scalar(
            select(User).where(User.email == user_in.email)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update password if provided
    if user_in.password:
        user_in.password = get_password_hash(user_in.password)
    
    # Update user fields
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> None:
    """Delete user (superuser only)."""
    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own user account"
        )
    
    # Delete user
    await db.delete(user)
    await db.commit()