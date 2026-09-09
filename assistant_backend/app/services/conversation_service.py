from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message, RoleEnum

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(self, conversation_id: str | None = None) -> Conversation:
        if conversation_id:
            conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                return conversation
        
        # Create a new conversation
        new_conversation = Conversation(title="New Chat")
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        return new_conversation

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=RoleEnum(role),
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_conversation_history(self, conversation_id: str) -> list[dict]:
        """
        Returns history formatted for Ollama: [{"role": "...", "content": "..."}]
        """
        messages = self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
