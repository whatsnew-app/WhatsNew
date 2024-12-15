# app/api/v1/endpoints/prompts.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.models.user import User
from app.models.prompt import Prompt, PromptType
from app.models.prompt_template import PromptTemplate
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
    """Create a new prompt."""
    # First verify template exists
    template_query = select(PromptTemplate).where(PromptTemplate.id == prompt_in.template_id)
    template = await db.scalar(template_query)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    prompt = Prompt(
        **prompt_in.dict(),
        user_id=current_user.id
    )
    db.add(prompt)
    
    try:
        await db.commit()
        # Explicitly load the template relationship
        await db.refresh(prompt, ['template'])
        return prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating prompt: {str(e)}"
        )

@router.get("/", response_model=List[PromptSchema])
async def get_prompts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    prompt_type: Optional[PromptType] = None,
    current_user: User = Depends(get_current_user)
) -> List[Prompt]:
    """Get all accessible prompts."""
    # Build query with eager loading of template
    query = (
        select(Prompt)
        .options(joinedload(Prompt.template))
    )
    
    if prompt_type:
        query = query.where(Prompt.type == prompt_type)
    
    if not current_user.is_superuser:
        query = query.where(
            (Prompt.type == PromptType.PUBLIC) |
            (Prompt.type == PromptType.INTERNAL) |
            ((Prompt.type == PromptType.PRIVATE) & (Prompt.user_id == current_user.id))
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()

@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Prompt:
    """Get a specific prompt."""
    query = (
        select(Prompt)
        .options(joinedload(Prompt.template))
        .where(Prompt.id == prompt_id)
    )
    prompt = await db.scalar(query)
    
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    if prompt.type == PromptType.PRIVATE and prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    return prompt

@router.put("/{prompt_id}", response_model=PromptSchema)
async def update_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    prompt_in: PromptUpdate,
    current_user: User = Depends(get_current_user)
) -> Prompt:
    """Update a specific prompt."""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    update_data = prompt_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    try:
        await db.commit()
        await db.refresh(prompt, ['template'])
        return prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating prompt: {str(e)}"
        )

@router.delete("/{prompt_id}")
async def delete_prompt(
    *,
    db: AsyncSession = Depends(get_db),
    prompt_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete a specific prompt."""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    if prompt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    try:
        await db.delete(prompt)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting prompt: {str(e)}"
        )

    return {"message": "Prompt deleted successfully"}