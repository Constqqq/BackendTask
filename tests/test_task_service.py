import pytest
from unittest.mock import MagicMock
from services.task_service import TaskService
from schemas.task import TaskCreate
from database.models import Task

@pytest.fixture
def mock_db():
    class DummySession:
        def __init__(self):
            self.added = None
            self.committed = False
            self.refreshed = None
        def add(self, obj):
            self.added = obj
        def commit(self):
            self.committed = True
        def refresh(self, obj):
            self.refreshed = obj
    return DummySession()

def test_create_task(mock_db):
    service = TaskService(mock_db)
    task_data = TaskCreate(title="Test", description="Desc", status="pending")
    user_id = 1
    result = service.create_task(task_data, user_id)
    assert isinstance(result, Task)
    assert result.title == "Test"
    assert result.description == "Desc"
    assert result.status == "pending"
    assert result.user_id == 1
    assert mock_db.added == result
    assert mock_db.committed
    assert mock_db.refreshed == result
