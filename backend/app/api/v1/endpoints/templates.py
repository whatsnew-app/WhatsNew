# app/api/v1/endpoints/templates.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

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

@router.post(
    "/admin/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)]
)
async def create_template(
    template: TemplateCreate,
    db: AsyncSession = Depends(get_db)
) -> PromptTemplate:
    """Create a new prompt template."""
    db_template = PromptTemplate(
        name=template.name,
        description=template.description,
        template_content=template.template_content,  # Changed from content to template_content
        is_active=template.is_active
    )
    
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get(
    "/admin/templates",
    response_model=List[TemplateResponse],
    dependencies=[Depends(get_current_superuser)]
)
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[PromptTemplate]:
    """List all prompt templates."""
    templates = await db.scalars(
        select(PromptTemplate)
        .offset(skip)
        .limit(limit)
    )
    return templates.all()

@router.get(
    "/admin/templates/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> PromptTemplate:
    """Get a specific prompt template."""
    template = await db.get(PromptTemplate, template_id)
    if not template:
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
    template_update: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
) -> PromptTemplate:
    """Update a prompt template."""
    template = await db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template

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
    template = await db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await db.delete(template)
    await db.commit()