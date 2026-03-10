from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db, is_postgres, in_memory_tasks, InMemoryTask
from database.models import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if is_postgres:
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status
        )
    else:
        db_task = InMemoryTask(
            title=task.title,
            description=task.description,
            status=task.status
        )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    if is_postgres:
        return db.query(Task).all()
    else:
        return in_memory_tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id), None)
    
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
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if is_postgres:
        task = db.query(Task).filter(Task.id == task_id).first()
    else:
        task = next((t for t in in_memory_tasks if t.id == task_id), None)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
