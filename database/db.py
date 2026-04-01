from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from datetime import datetime
import os

POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:6080@localhost:5432/BackTask2"
)

POSTGRES_SYNC_URL = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql://postgres:6080@localhost:5432/BackTask2"
)

engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None
Base = declarative_base()
is_postgres = False

in_memory_tasks = []
in_memory_task_id_counter = 1

try:
    async_engine = create_async_engine(
        POSTGRES_URL,
        echo=False,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    try:
        sync_engine = create_engine(POSTGRES_SYNC_URL, pool_pre_ping=True)
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = sync_engine
        is_postgres = True
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        print("Connected to PostgreSQL")
    except (OperationalError, Exception) as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Using in-memory storage...")
        is_postgres = False
except (OperationalError, Exception) as e:
    print(f"Async PostgreSQL connection initial setup failed: {e}")
    print("Using in-memory storage...")
    is_postgres = False


class InMemorySession:
    def query(self, model):
        return InMemoryQuery(model)
    
    def add(self, task_obj):
        global in_memory_task_id_counter
        if not task_obj.id:
            task_obj.id = in_memory_task_id_counter
            in_memory_task_id_counter += 1
        in_memory_tasks.append(task_obj)
    
    def commit(self):
        pass
    
    def refresh(self, obj):
        pass
    
    def delete(self, obj):
        global in_memory_tasks
        in_memory_tasks = [t for t in in_memory_tasks if t.id != obj.id]
    
    def close(self):
        pass


class InMemoryQuery:
    def __init__(self, model):
        self.model = model
    
    def all(self):
        return in_memory_tasks
    
    def filter(self, condition):
        return InMemoryFilterQuery(condition, in_memory_tasks)
    
    def first(self):
        return in_memory_tasks[0] if in_memory_tasks else None


class InMemoryFilterQuery:
    def __init__(self, condition, data):
        self.condition = condition
        self.data = data
    
    def first(self):
        for task in self.data:
            if hasattr(self.condition, "left") and hasattr(self.condition, "right"):
                if self.condition.right.value == task.id:
                    return task
        return None


class InMemoryTask:
    def __init__(self, title, description, status, user_id):
        self.id = None
        self.title = title
        self.description = description
        self.status = status
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


def get_db():
    if is_postgres:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield InMemorySession()


async def get_async_db():
    if is_postgres and AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        yield InMemorySession()


async def verify_db_connection():
    if is_postgres and async_engine:
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    elif is_postgres and engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    else:
        return False
