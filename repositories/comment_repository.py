from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_comments_by_task_id(self, task_id: int) -> list[Comment]:
        result = await self.db.execute(select(Comment).filter(Comment.task_id == task_id))
        return result.scalars().all()

    async def create_comment(self, task_id: int, content: str) -> Comment:
        db_comment = Comment(content=content, task_id=task_id)
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment
