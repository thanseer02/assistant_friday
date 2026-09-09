from pydantic import BaseModel
from typing import Optional
from app.schemas.action import ActionRequest

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    pending_action: Optional[ActionRequest] = None

