from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MemoryCreate(BaseModel):
    key: str
    value: str
    category: Optional[str] = None

class MemorySchema(MemoryCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
