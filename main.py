from fastapi import FastAPI
from database.db import engine, Base, is_postgres
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router

if is_postgres and engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tasks_router)
app.include_router(auth_router)
