from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User
from utils.security import get_password_hash, verify_password
from schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()
    
    async def create_user(self, user_create: UserCreate) -> User:
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=1
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def verify_user_password(self, user: User, password: str) -> bool:
        return verify_password(password, user.hashed_password)
    
    async def update_user(self, user_id: int, **kwargs) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            await self.db.commit()
            return True
        return False
