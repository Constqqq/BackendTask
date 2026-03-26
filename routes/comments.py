from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db, is_postgres
from database.models import Task, Comment, User
from schemas.comment import CommentCreate, CommentOut
from repositories.comment_repository import CommentRepository
from .tasks import get_current_user
 
router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])
 
 
@router.post("", response_model=CommentOut)
def create_comment(task_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        repo = CommentRepository(db)
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db_comment = repo.create_comment(task_id=task_id, content=comment.content)
        return db_comment
    else:
        raise HTTPException(status_code=501, detail="In-memory comments not implemented")
 
 
@router.get("", response_model=list[CommentOut])
def get_comments(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        repo = CommentRepository(db)
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
       
        return repo.get_comments_by_task_id(task_id=task_id)
    else:
        raise HTTPException(status_code=501, detail="In-memory comments not implemented")