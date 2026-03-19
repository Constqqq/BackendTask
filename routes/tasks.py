from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.db import get_db, is_postgres, in_memory_tasks, InMemoryTask
from database.models import Task, User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from repositories.user_repository import UserRepository
from utils.security import verify_token

router = APIRouter(prefix="/tasks", tags=["tasks"])
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    email = payload.get("sub") if isinstance(payload, dict) else None
    if not isinstance(email, str) or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return user


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            user_id=current_user.id
        )
    else:
        db_task = InMemoryTask(
            title=task.title,
            description=task.description,
            status=task.status,
            user_id=current_user.id
        )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=list[TaskResponse])
def get_all_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        return db.query(Task).filter(Task.user_id == current_user.id).all()
    else:
        return [t for t in in_memory_tasks if t.user_id == current_user.id]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id and t.user_id == current_user.id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id and t.user_id == current_user.id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id and t.user_id == current_user.id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
