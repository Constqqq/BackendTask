from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
 
 
class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: str = Field(default="pending")
 
 
class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None)
 
 
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
 