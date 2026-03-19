from sqlalchemy.orm import Session
from database.models import User
from utils.security import get_password_hash, verify_password
from schemas.user import UserCreate


class UserRepository:
    
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> User | None:
        
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> User | None:
        
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self) -> list[User]:
       
        return self.db.query(User).all()
    
    def create_user(self, user_create: UserCreate) -> User:
        
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=1
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def verify_user_password(self, user: User, password: str) -> bool:
        
        return verify_password(password, user.hashed_password)
    
    def update_user(self, user_id: int, **kwargs) -> User | None:
        
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
