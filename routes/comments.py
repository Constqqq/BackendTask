from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_async_db, is_postgres
from database.models import Task, Comment, User
from schemas.comment import CommentCreate, CommentOut
from repositories.comment_repository import CommentRepository
from .tasks import get_current_user
 
router = APIRouter(prefix="/v1/tasks/{task_id}/comments", tags=["comments"])
 
 
@router.post("", response_model=CommentOut)
async def create_comment(task_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    if is_postgres:
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        repo = CommentRepository(db)
        db_comment = await repo.create_comment(task_id=task_id, content=comment.content)
        return db_comment
    else:
        raise HTTPException(status_code=501, detail="In-memory comments not implemented")
 
 
@router.get("", response_model=list[CommentOut])
async def get_comments(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    if is_postgres:
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        repo = CommentRepository(db)
        return await repo.get_comments_by_task_id(task_id=task_id)
    else:
        raise HTTPException(status_code=501, detail="In-memory comments not implemented")
