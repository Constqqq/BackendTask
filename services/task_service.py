from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Task
from schemas.task import TaskCreate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            user_id=user_id
        )
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task
    
    async def get_task_by_id(self, task_id: int, user_id: int) -> Task | None:
        result = await self.db.execute(
            select(Task).filter(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_tasks_for_user(self, user_id: int) -> list[Task]:
        result = await self.db.execute(
            select(Task).filter(Task.user_id == user_id)
        )
        return result.scalars().all()
    
    async def update_task(self, task_id: int, user_id: int, **kwargs) -> Task | None:
        task = await self.get_task_by_id(task_id, user_id)
        if task:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(task, key, value)
            await self.db.commit()
            await self.db.refresh(task)
        return task
    
    async def delete_task(self, task_id: int, user_id: int) -> bool:
        task = await self.get_task_by_id(task_id, user_id)
        if task:
            self.db.delete(task)
            await self.db.commit()
            return True
        return False
