# app/api/v1/endpoints/prompts.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.api.deps import get_current_user, get_current_superuser, get_db, get_current_active_user
from app.models.user import User
from app.models.prompt import Prompt, PromptType
from app.schemas.prompt import (
    Prompt as PromptSchema,
    PromptCreate,
    PromptUpdate,
    PromptList,
    PromptResponse
)

router = APIRouter()

@router.post("/", response_model=PromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_in: PromptCreate,
    current_user: User = Depends(get_current_active_user)
) -> Prompt:
    """Create a new prompt."""
    prompt = Prompt(
        **prompt_in.dict(),
        user_id=current_user.id
    )
    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)
    return prompt

@router.get("/", response_model=List[PromptSchema])
async def get_prompts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    prompt_type: Optional[PromptType] = None,
    current_user: User = Depends(get_current_active_user)
) -> List[Prompt]:
    """Get all accessible prompts with filtering."""
    query = select(Prompt)
    
    if prompt_type:
        query = query.where(Prompt.type == prompt_type)
    
    if not current_user.is_superuser:
        query = query.where(
            (Prompt.type == PromptType.PUBLIC) |
            (Prompt.type == PromptType.INTERNAL) |
            ((Prompt.type == PromptType.PRIVATE) & (Prompt.user_id == current_user.id))
        )
    
    prompts = await db.scalars(
        query.offset(skip).limit(limit)
    )
    return prompts.all()

@router.get("/internal", response_model=List[PromptResponse])
async def list_internal_prompts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Prompt]:
    """List all internal prompts available to logged-in users."""
    query = (
        select(Prompt)
        .where(Prompt.type == PromptType.INTERNAL)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    prompts = result.scalars().all()
    return prompts

@router.get("/my", response_model=PromptList)
async def list_user_prompts(
    skip: int = 0,
    limit: int = 100,
    prompt_type: Optional[PromptType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> PromptList:
    """List prompts owned by current user."""
    query = select(Prompt).where(Prompt.user_id == current_user.id)
    
    if prompt_type:
        query = query.where(Prompt.type == prompt_type)
    
    total = await db.scalar(
        select(func.count(Prompt.id))
        .where(Prompt.user_id == current_user.id)
        .where(Prompt.type == prompt_type if prompt_type else True)
    )
    
    prompts = await db.scalars(
        query.offset(skip).limit(limit)
    )
    
    return PromptList(
        items=prompts.all(),
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Prompt:
    """Get a specific prompt by ID."""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    if (prompt.type == PromptType.PRIVATE and 
        prompt.user_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return prompt

@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    prompt_in: PromptUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Prompt:
    """Update a prompt."""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = prompt_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)
    
    await db.commit()
    await db.refresh(prompt)
    return prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """Delete a prompt."""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(prompt)
    await db.commit()