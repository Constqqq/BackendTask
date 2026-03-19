from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=255, description="User password")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
