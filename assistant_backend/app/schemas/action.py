from pydantic import BaseModel
from typing import Any

class ActionRequest(BaseModel):
    id: str
    tool_name: str
    arguments: dict[str, Any]
    status: str
    conversation_id: str

    class Config:
        from_attributes = True
