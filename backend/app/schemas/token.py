# app/schemas/token.py

from pydantic import BaseModel

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str

class TokenData(BaseModel):
    """Token payload schema."""
    sub: str | None = None
    refresh: bool = False