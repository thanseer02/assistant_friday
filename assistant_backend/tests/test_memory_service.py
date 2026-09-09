import pytest
from unittest.mock import MagicMock
from app.services.memory_service import MemoryService
from app.models.memory import Memory

@pytest.fixture
def db_session_mock():
    return MagicMock()

@pytest.fixture
def memory_service(db_session_mock):
    return MemoryService(db_session_mock)

def test_save_memory_new(memory_service, db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    mem = memory_service.save_memory("favorite color", "blue", "preference")
    assert mem.key == "favorite color"
    assert mem.value == "blue"
    assert mem.category == "preference"
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()

def test_save_memory_existing(memory_service, db_session_mock):
    existing = Memory(key="favorite color", value="red", category="preference")
    db_session_mock.query.return_value.filter.return_value.first.return_value = existing
    
    mem = memory_service.save_memory("favorite color", "blue", "preference")
    assert mem.value == "blue"  # Updated value
    db_session_mock.add.assert_not_called()
    db_session_mock.commit.assert_called_once()

def test_search_memories(memory_service, db_session_mock):
    mock_memory = Memory(key="project name", value="Jarvis")
    db_session_mock.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_memory]
    
    results = memory_service.search_memories("What is my project name?")
    assert len(results) == 1
    assert results[0].value == "Jarvis"

def test_search_memories_empty_query(memory_service, db_session_mock):
    results = memory_service.search_memories("is a") # Short words get filtered out
    assert len(results) == 0
    db_session_mock.query.assert_not_called()
