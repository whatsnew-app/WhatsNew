# cli.py

import asyncio
import typer
from sqlalchemy import select, text
from app.core.config import settings
from app.core.database import async_session
from app.core.security import get_password_hash
from app.models.base import User  # Import from base instead

app = typer.Typer(help="News Summarizer CLI")


async def check_db_connection():
    """Test database connection."""
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
            return True
    except Exception as e:
        typer.echo(f"Database connection failed: {e}")
        return False

async def create_superuser():
    """Create a superuser in the database."""
    # Check environment variables
    if not settings.FIRST_SUPERUSER_EMAIL or not settings.FIRST_SUPERUSER_PASSWORD:
        typer.echo("Error: FIRST_SUPERUSER_EMAIL and FIRST_SUPERUSER_PASSWORD must be set in .env")
        raise typer.Exit(1)

    # Check database connection
    if not await check_db_connection():
        typer.echo("Error: Could not connect to database")
        raise typer.Exit(1)

    try:
        async with async_session() as db:
            # Check if superuser exists
            result = await db.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                typer.echo(f"Superuser {settings.FIRST_SUPERUSER_EMAIL} already exists")
                return

            # Create new superuser
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True,
                full_name="System Administrator"
            )
            
            db.add(superuser)
            await db.commit()
            typer.echo(f"Superuser {settings.FIRST_SUPERUSER_EMAIL} created successfully")

    except Exception as e:
        typer.echo(f"Error creating superuser: {e}")
        raise typer.Exit(1)

@app.command()
def createsuperuser():
    """Create a new superuser account using environment variables."""
    try:
        asyncio.run(create_superuser())
    except Exception as e:
        typer.echo(f"Unexpected error: {e}")
        raise typer.Exit(1)

@app.command()
def dbcheck():
    """Check database connection."""
    try:
        result = asyncio.run(check_db_connection())
        if result:
            typer.echo("Database connection successful!")
        else:
            typer.echo("Database connection failed!")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error checking database: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()