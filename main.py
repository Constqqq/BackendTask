from fastapi import FastAPI
from database.db import engine, Base, is_postgres
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.comments import router as comments_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException

if is_postgres and engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI()


_ERROR_CODES = {
    "Task not found": "TaskNotFound",
    "Comment not found": "CommentNotFound",
}


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.detail in _ERROR_CODES:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": _ERROR_CODES[exc.detail],
                    "message": exc.detail,
                }
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(comments_router)