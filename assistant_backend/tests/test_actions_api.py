import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app

@pytest.fixture
def mock_action_service():
    with patch("app.api.actions.ActionPermissionService") as mock:
        instance = mock.return_value
        mock_action = MagicMock()
        mock_action.status = "pending"
        mock_action.tool_name = "create_reminder"
        mock_action.arguments = {"reminder": "Test"}
        mock_action.conversation_id = "conv123"
        instance.get_action.return_value = mock_action
        yield instance

@pytest.fixture
def mock_ai_service_actions():
    with patch("app.api.actions.AIService") as mock:
        instance = mock.return_value
        instance.generate_response = AsyncMock(return_value="Action processed.")
        yield instance

@pytest.fixture
def mock_conversation_service_actions():
    with patch("app.api.actions.ConversationService") as mock:
        yield mock.return_value

@pytest.fixture
def mock_tool_registry():
    with patch("app.api.actions.tool_registry") as mock:
        mock.execute_tool = AsyncMock(return_value="Success")
        yield mock

@pytest.mark.asyncio
async def test_approve_action(mock_action_service, mock_ai_service_actions, mock_conversation_service_actions, mock_tool_registry):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/actions/action123/approve")
    
    assert response.status_code == 200
    assert response.json()["response"] == "Action processed."
    
    mock_action_service.update_action_status.assert_called_once_with("action123", "approved")
    mock_tool_registry.execute_tool.assert_called_once_with("create_reminder", {"reminder": "Test"})
    mock_conversation_service_actions.add_message.assert_any_call("conv123", "tool", "Success")

@pytest.mark.asyncio
async def test_reject_action(mock_action_service, mock_ai_service_actions, mock_conversation_service_actions):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/actions/action123/reject")
    
    assert response.status_code == 200
    assert response.json()["response"] == "Action processed."
    
    mock_action_service.update_action_status.assert_called_once_with("action123", "rejected")
    mock_conversation_service_actions.add_message.assert_any_call("conv123", "tool", "Error: User rejected the action.")
