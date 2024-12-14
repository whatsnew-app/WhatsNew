import re
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def generate_news_slug(
    title: str,
    prompt_name: str,
    date: datetime,
    db: Optional[AsyncSession] = None
) -> str:
    """Generate a URL-friendly slug for news articles"""
    # Clean the title
    slug = title.lower()
    
    # Replace special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    
    # Format the date
    date_str = date.strftime('%Y-%m-%d')
    
    # Clean prompt name
    clean_prompt_name = re.sub(r'[^\w\s-]', '', prompt_name.lower())
    clean_prompt_name = re.sub(r'[\s_-]+', '-', clean_prompt_name)
    clean_prompt_name = clean_prompt_name.strip('-')
    
    # Combine all parts
    base_slug = f"{clean_prompt_name}/{date_str}/{slug}"
    
    if not db:
        return base_slug
    
    # Check for duplicates if db is provided
    counter = 1
    final_slug = base_slug
    
    # Import here to avoid circular imports
    from app.models.news import NewsArticle
    
    while True:
        # Check if slug exists
        exists = await db.scalar(
            select(NewsArticle).where(NewsArticle.slug == final_slug)
        )
        
        if not exists:
            break
            
        # Add counter to slug
        final_slug = f"{base_slug}-{counter}"
        counter += 1
    
    return final_slug

def is_valid_slug(slug: str) -> bool:
    """Validate if a slug follows the correct format"""
    pattern = r'^[\w-]+/\d{4}-\d{2}-\d{2}/[\w-]+$'
    return bool(re.match(pattern, slug))

def extract_date_from_slug(slug: str) -> Optional[datetime]:
    """Extract date from a slug"""
    try:
        parts = slug.split('/')
        if len(parts) != 3:
            return None
        
        date_str = parts[1]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, IndexError):
        return None

def extract_prompt_name_from_slug(slug: str) -> Optional[str]:
    """Extract prompt name from a slug"""
    try:
        return slug.split('/')[0]
    except IndexError:
        return None