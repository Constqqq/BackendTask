import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

from main import app

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def _register_and_login(email="test@example.com", password="testpassword123"):
    """Вспомогательная функция: регистрация + получение токена."""
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.json()}"
    return resp.json()["access_token"]


def test_create_task_integration():
    """Интеграционный тест: создание задачи с авторизацией."""
    token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    data = {"title": "Integration Task", "description": "desc", "status": "pending"}
    response = client.post("/tasks", json=data, headers=headers)

    assert response.status_code == 200
    result = response.json()
    assert result["title"] == "Integration Task"
    assert result["description"] == "desc"
    assert result["status"] == "pending"
    assert "id" in result
    assert "created_at" in result


def test_create_task_unauthorized():
    """Без токена должен быть 401."""
    data = {"title": "Task", "description": "desc", "status": "pending"}
    response = client.post("/tasks", json=data)
    assert response.status_code == 401


def test_task_not_found_error_format():
    """TaskNotFound должен возвращать правильный формат error."""
    token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/tasks/99999", headers=headers)
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "TaskNotFound"
    assert body["error"]["message"] == "Task not found"