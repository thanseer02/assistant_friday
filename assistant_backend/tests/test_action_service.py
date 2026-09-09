import pytest
from unittest.mock import MagicMock
from app.services.action_service import ActionPermissionService
from app.models.action import PendingAction

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def action_service(mock_db):
    return ActionPermissionService(mock_db)

def test_create_pending_action(action_service, mock_db):
    action = action_service.create_pending_action("conv123", "send_msg", {"msg": "hi"})
    assert action.conversation_id == "conv123"
    assert action.tool_name == "send_msg"
    assert action.arguments == {"msg": "hi"}
    assert action.status == "pending"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_update_action_status(action_service, mock_db):
    mock_action = PendingAction(status="pending")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_action
    
    updated = action_service.update_action_status("id123", "approved")
    assert updated.status == "approved"
    mock_db.commit.assert_called_once()
