from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.memory import Memory

class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def save_memory(self, key: str, value: str, category: str | None = None) -> Memory:
        # Check if memory with key already exists to update it
        existing = self.db.query(Memory).filter(Memory.key == key).first()
        if existing:
            existing.value = value
            existing.category = category
            self.db.commit()
            self.db.refresh(existing)
            return existing

        new_memory = Memory(key=key, value=value, category=category)
        self.db.add(new_memory)
        self.db.commit()
        self.db.refresh(new_memory)
        return new_memory

    def get_memory(self, memory_id: str) -> Memory | None:
        return self.db.query(Memory).filter(Memory.id == memory_id).first()

    def get_all_memories(self) -> list[Memory]:
        return self.db.query(Memory).order_by(Memory.created_at.desc()).all()

    def delete_memory(self, memory_id: str) -> bool:
        memory = self.get_memory(memory_id)
        if memory:
            self.db.delete(memory)
            self.db.commit()
            return True
        return False

    def search_memories(self, query: str) -> list[Memory]:
        """
        Simple keyword search for SQLite. 
        Splits query into words and searches for matches in key or value.
        """
        words = [w for w in query.split() if len(w) > 3] # Ignore small words
        if not words:
            return []
            
        filters = []
        for word in words:
            filters.append(Memory.key.ilike(f"%{word}%"))
            filters.append(Memory.value.ilike(f"%{word}%"))
            
        return self.db.query(Memory).filter(or_(*filters)).limit(5).all()
