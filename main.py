from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from database.db import engine, Base, is_postgres
from routes.tasks import router as tasks_router, minio_client
from routes.auth import router as auth_router
from routes.comments import router as comments_router
from utils.health import check_health, get_info

if is_postgres and engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="BackendTask API", version="1.0.0")


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


@app.get("/health")
async def health():
    return await check_health(minio_client)


@app.get("/info")
async def info():
    return get_info()
