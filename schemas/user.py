from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=255, description="User password")


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None