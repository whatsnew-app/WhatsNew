from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.models.user import User
from app.models.prompt import Prompt, PromptType
from app.schemas.prompt import (
    Prompt as PromptSchema,
    PromptCreate,
    PromptUpdate
)

router = APIRouter()

@router.post("/", response_model=PromptSchema)
async def create_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_in: PromptCreate,
    current_user: User = Depends(get_current_user)
) -> Prompt:
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
    current_user: User = Depends(get_current_user)
) -> List[Prompt]:
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

@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Prompt:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if (prompt.type == PromptType.PRIVATE and 
        prompt.user_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return prompt

@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    prompt_in: PromptUpdate,
    current_user: User = Depends(get_current_user)
) -> Prompt:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = prompt_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)
    
    await db.commit()
    await db.refresh(prompt)
    return prompt

@router.delete("/{prompt_id}")
async def delete_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
) -> dict:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await db.delete(prompt)
    await db.commit()
    
    return {"message": "Prompt deleted successfully"}