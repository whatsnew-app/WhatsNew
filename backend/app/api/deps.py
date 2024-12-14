# app/api/deps.py

from typing import AsyncGenerator, Optional, Union, Annotated
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = await verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await db.scalar(
        select(User).where(User.id == user_id)
    )
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_websocket_user(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get user from WebSocket connection."""
    try:
        # Get token from query parameters or headers
        token = websocket.query_params.get("token") or \
                websocket.headers.get("authorization", "").replace("Bearer ", "")
        
        if not token:
            return None
            
        payload = await verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        user = await db.scalar(
            select(User).where(User.id == user_id)
        )
        return user if user and user.is_active else None
        
    except Exception:
        return None

async def validate_task_access(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Task:
    """Validate task access for current user."""
    task = await db.scalar(
        select(Task).where(Task.id == task_id)
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    # Only superusers and task creators can access tasks
    if not current_user.is_superuser and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
        
    return task

async def get_rate_limit_key(
    current_user: Optional[User] = Depends(get_current_user)
) -> str:
    """Get rate limit key for current user or IP."""
    return f"rate_limit:{current_user.id if current_user else 'anonymous'}"

async def check_task_status(task: Task) -> Task:
    """Check if task is in valid state for operations."""
    if task.status in [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is already {task.status}"
        )
    return task

CommonDependencies = Annotated[
    tuple[AsyncSession, User],
    Depends(lambda: (
        Depends(get_db),
        Depends(get_current_active_user)
    ))
]

SuperuserDependencies = Annotated[
    tuple[AsyncSession, User],
    Depends(lambda: (
        Depends(get_db),
        Depends(get_current_superuser)
    ))
]