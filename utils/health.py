from pydantic import BaseModel
from typing import Optional
from database.db import verify_db_connection
from utils.minio_client import MinIOClient
import os


class HealthStatus(BaseModel):
    status: str
    database: bool
    minio: bool


class InfoResponse(BaseModel):
    version: str
    environment: str
    name: str


async def check_health(minio_client: Optional[MinIOClient] = None) -> HealthStatus:
    db_ok = await verify_db_connection()
    minio_ok = False
    
    if minio_client:
        minio_ok = await minio_client.check_connection()
    
    status = "healthy" if (db_ok and minio_ok) else "degraded"
    
    return HealthStatus(
        status=status,
        database=db_ok,
        minio=minio_ok
    )


def get_info() -> InfoResponse:
    return InfoResponse(
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        name="BackendTask API"
    )
