import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app

@pytest.fixture
def mock_ai_service():
    with patch("app.api.chat.AIService") as mock:
        instance = mock.return_value
        instance.generate_response = AsyncMock(return_value="Nice to meet you, Alex!")
        instance.extract_memories = AsyncMock(return_value=[])
        yield instance

@pytest.fixture
def mock_conversation_service():
    with patch("app.api.chat.ConversationService") as mock:
        instance = mock.return_value
        
        # Mock getting conversation
        mock_conv = MagicMock()
        mock_conv.id = "test-conv-id"
        instance.get_or_create_conversation.return_value = mock_conv
        
        # Mock getting history
        instance.get_conversation_history.return_value = [{"role": "user", "content": "My name is Alex"}]
        
        yield instance

@pytest.fixture
def mock_memory_service():
    with patch("app.api.chat.MemoryService") as mock:
        instance = mock.return_value
        instance.search_memories.return_value = []
        yield instance

@pytest.mark.asyncio
async def test_chat_endpoint(mock_ai_service, mock_conversation_service, mock_memory_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={"message": "My name is Alex", "conversation_id": None})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Nice to meet you, Alex!"
    assert data["conversation_id"] == "test-conv-id"
    
    mock_conversation_service.get_or_create_conversation.assert_called_once_with(None)
    mock_conversation_service.add_message.assert_any_call("test-conv-id", "user", "My name is Alex")
    mock_conversation_service.add_message.assert_any_call("test-conv-id", "assistant", "Nice to meet you, Alex!")
    
    # We pass an empty list of memories since we mock search_memories to return []
    # Using ANY for tool_registry since it's the global instance
    from unittest.mock import ANY
    mock_ai_service.generate_response.assert_called_once_with(
        [{"role": "user", "content": "My name is Alex"}], 
        memories=[],
        tool_registry=ANY
    )
