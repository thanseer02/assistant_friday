from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class IncomingMessage(BaseModel):
    platform: str
    platform_user_id: str
    conversation_id: str
    text: str
    timestamp: datetime
    metadata: Optional[dict[str, Any]] = None

class OutgoingMessage(BaseModel):
    platform: str
    platform_user_id: str
    conversation_id: str
    text: str
    metadata: Optional[dict[str, Any]] = None
