from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime, timezone
import uuid

from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    key = Column(String, index=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
