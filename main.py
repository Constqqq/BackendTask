from fastapi import FastAPI
from database.db import engine, Base, is_postgres
from routes.tasks import router as tasks_router

if is_postgres and engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tasks_router)


# @app.get("/")
# def read_root():
#     return {"message": "Task Management API"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
