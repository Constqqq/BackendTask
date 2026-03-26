from database.models import Task
from sqlalchemy.orm import Session
from schemas.task import TaskCreate

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: TaskCreate, user_id: int) -> Task:
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            user_id=user_id
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
