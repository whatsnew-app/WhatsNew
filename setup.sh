#!/bin/bash

# Create main project directory
mkdir -p WhatsNews
cd WhatsNews

# Create README and other documentation
cat > README.md << 'EOF'
# WhatsNews 🌐

WhatsNews is an open-source AI-powered news summarization platform...
[Previous README content will go here]
EOF

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 WhatsNews

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
EOF

# Create project structure
mkdir -p {alembic/versions,app/{core,api/v1/endpoints,models,schemas,services,tasks,utils},tests/{test_api,test_services}}

# Create __init__.py files
find . -type d -not -path "./venv*" -not -path "./.git*" -exec touch {}/__init__.py \;

# Create core files
cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "News Summarizer API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for news summarization with AI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Default superuser
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create main application file
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
EOF

# Create environment files
cat > .env.example << 'EOF'
# API Settings
PROJECT_NAME=News Summarizer API
VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/news_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=adminpassword

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
STABILITY_API_KEY=your-stability-key
EOF

cp .env.example .env

# Create requirements files
cat > requirements.txt << 'EOF'
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.11.0
asyncpg>=0.27.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
celery>=5.3.0
redis>=4.5.0
httpx>=0.24.0
python-dateutil>=2.8.2
email-validator>=2.0.0
openai>=1.0.0
anthropic>=0.3.0
pillow>=10.0.0
feedparser>=6.0.0
EOF

cat > requirements-dev.txt << 'EOF'
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.4.0
EOF

# Create Docker files
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/news_db
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=news_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6

volumes:
  postgres_data:
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env

# Logs
*.log

# Database
*.sqlite3

# Coverage
.coverage
htmlcov/

# Celery
celerybeat-schedule
celerybeat.pid
EOF

# Create initial alembic files
cat > alembic.ini << 'EOF'
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF



echo "Project structure created successfully!"
echo "Next steps:"
echo "1. Create and activate a virtual environment"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Configure your .env file"
echo "4. Initialize the database with alembic"
echo "5. Run the development server: uvicorn main:app --reload"