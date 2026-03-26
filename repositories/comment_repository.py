from sqlalchemy.orm import Session
from database.models import Comment

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_comments_by_task_id(self, task_id: int) -> list[Comment]:
        return self.db.query(Comment).filter(Comment.task_id == task_id).all()

    def create_comment(self, task_id: int, content: str) -> Comment:
        db_comment = Comment(content=content, task_id=task_id)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
