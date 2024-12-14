from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password
)
from app.core.config import settings
from app.api.deps import get_db
from app.schemas.user import User, UserCreate
from app.models.user import User as UserModel
from sqlalchemy import select

router = APIRouter()

@router.post("/login")
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = await db.scalar(
        select(UserModel).where(UserModel.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate
) -> Any:
    user = await db.scalar(
        select(UserModel).where(UserModel.email == user_in.email)
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    user = UserModel(
        email=user_in.email,
        password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user