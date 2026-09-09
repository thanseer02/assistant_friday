from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.models.conversation import RoleEnum

class MessageSchema(BaseModel):
    id: str
    conversation_id: str
    role: RoleEnum
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationSchema(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []

    model_config = ConfigDict(from_attributes=True)

class ConversationListSchema(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
