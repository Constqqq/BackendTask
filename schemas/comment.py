from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    task_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None