# app/api/v1/endpoints/templates.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_superuser
from app.models.prompt_template import PromptTemplate
from app.models.user import User
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateList
)

router = APIRouter()

@router.get(
    "/admin/templates",
    response_model=List[TemplateResponse],
    dependencies=[Depends(get_current_superuser)]
)
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all prompt templates."""
    query = select(PromptTemplate).offset(skip).limit(limit)
    result = await db.execute(query)
    templates = result.scalars().all()
    return templates

@router.post(
    "/admin/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)]
)
async def create_template(
    template: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create a new prompt template."""
    db_template = PromptTemplate(
        name=template.name,
        description=template.description,
        template_content=template.content,
        is_active=template.is_active
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get(
    "/admin/templates/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific prompt template."""
    query = select(PromptTemplate).where(PromptTemplate.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template

@router.put(
    "/admin/templates/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def update_template(
    template_id: UUID,
    template: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a prompt template."""
    query = select(PromptTemplate).where(PromptTemplate.id == template_id)
    result = await db.execute(query)
    db_template = result.scalar_one_or_none()
    
    if db_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update template fields
    update_data = template.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.delete(
    "/admin/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_superuser)]
)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a prompt template."""
    query = select(PromptTemplate).where(PromptTemplate.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    await db.delete(template)
    await db.commit()
    return None