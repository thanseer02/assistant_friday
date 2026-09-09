from pydantic import BaseModel
from typing import Optional, Any

class IncomingMessage(BaseModel):
    platform: str
    platform_user_id: str
    conversation_id: str
    text: str
    metadata: Optional[dict[str, Any]] = None
