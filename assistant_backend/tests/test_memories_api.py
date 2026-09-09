import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from app.main import app

@pytest.fixture
def mock_memory_service():
    with patch("app.api.memories.MemoryService") as mock:
        instance = mock.return_value
        
        mock_mem = MagicMock()
        mock_mem.id = "test-id"
        mock_mem.key = "test key"
        mock_mem.value = "test value"
        mock_mem.category = "fact"
        from datetime import datetime
        mock_mem.created_at = datetime.now()
        mock_mem.updated_at = datetime.now()
        
        instance.get_all_memories.return_value = [mock_mem]
        instance.delete_memory.return_value = True
        
        yield instance

@pytest.mark.asyncio
async def test_get_memories(mock_memory_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/memories")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["key"] == "test key"
    assert data[0]["value"] == "test value"

@pytest.mark.asyncio
async def test_delete_memory(mock_memory_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/api/memories/test-id")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_memory_service.delete_memory.assert_called_once_with("test-id")

@pytest.mark.asyncio
async def test_delete_memory_not_found(mock_memory_service):
    mock_memory_service.delete_memory.return_value = False
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/api/memories/invalid-id")
    
    assert response.status_code == 404
