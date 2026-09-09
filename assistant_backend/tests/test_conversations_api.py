import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest.fixture(autouse=True)
def mock_ai_service():
    with patch("app.api.chat.AIService") as mock:
        instance = mock.return_value
        instance.generate_response = AsyncMock(return_value="Mocked AI response")
        instance.extract_memories = AsyncMock(return_value=[])
        yield instance

client = TestClient(app)

def test_create_conversation_and_save_message():
    # Chat with no conversation ID -> creates one
    response = client.post("/api/chat", json={
        "message": "Hello, this is a test message"
    })
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    
    conv_id = data["conversation_id"]
    
    # Retrieve the conversation to check if messages were saved
    res_get = client.get(f"/api/conversations/{conv_id}")
    assert res_get.status_code == 200
    conv_data = res_get.json()
    assert conv_data["id"] == conv_id
    
    messages = conv_data.get("messages", [])
    # Should have at least user message and assistant message
    assert len(messages) >= 2
    assert any(m["role"] == "user" and "Hello, this is a test message" in m["content"] for m in messages)
    assert any(m["role"] == "assistant" for m in messages)

def test_continue_existing_conversation():
    # 1. Create a conversation
    res1 = client.post("/api/chat", json={"message": "First message"})
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]
    
    # 2. Continue the conversation
    res2 = client.post("/api/chat", json={
        "conversation_id": conv_id,
        "message": "Second message"
    })
    assert res2.status_code == 200
    assert res2.json()["conversation_id"] == conv_id
    
    # 3. Retrieve and verify messages
    res_get = client.get(f"/api/conversations/{conv_id}")
    conv_data = res_get.json()
    messages = conv_data.get("messages", [])
    
    user_contents = [m["content"] for m in messages if m["role"] == "user"]
    assert "First message" in user_contents
    assert "Second message" in user_contents

def test_invalid_conversation_id():
    response = client.post("/api/chat", json={
        "conversation_id": "invalid-uuid-1234",
        "message": "This should fail"
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_all_conversations():
    # Ensure at least one exists
    client.post("/api/chat", json={"message": "Temp msg"})
    
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]

def test_delete_conversation():
    # 1. Create a conversation
    res1 = client.post("/api/chat", json={"message": "Delete me please"})
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]
    
    # 2. Delete it
    res_del = client.delete(f"/api/conversations/{conv_id}")
    assert res_del.status_code == 204
    
    # 3. Verify it's gone
    res_get = client.get(f"/api/conversations/{conv_id}")
    assert res_get.status_code == 404

def test_delete_invalid_conversation():
    res = client.delete("/api/conversations/non-existent-id-999")
    assert res.status_code == 404
