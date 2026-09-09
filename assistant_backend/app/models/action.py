from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime, timezone
import uuid

from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class PendingAction(Base):
    __tablename__ = "pending_actions"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    conversation_id = Column(String, index=True, nullable=False)
    tool_name = Column(String, nullable=False)
    arguments = Column(JSON, nullable=False)
    status = Column(String, default="pending", index=True) # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
