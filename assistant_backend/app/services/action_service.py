from sqlalchemy.orm import Session
from app.models.action import PendingAction

class ActionPermissionService:
    def __init__(self, db: Session):
        self.db = db

    def create_pending_action(self, conversation_id: str, tool_name: str, arguments: dict) -> PendingAction:
        action = PendingAction(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments=arguments,
            status="pending"
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def get_action(self, action_id: str) -> PendingAction | None:
        return self.db.query(PendingAction).filter(PendingAction.id == action_id).first()

    def update_action_status(self, action_id: str, status: str) -> PendingAction | None:
        action = self.get_action(action_id)
        if action:
            action.status = status
            self.db.commit()
            self.db.refresh(action)
        return action
