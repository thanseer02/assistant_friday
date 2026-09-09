from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.memory import MemorySchema
from app.services.memory_service import MemoryService
from app.database.session import get_db

router = APIRouter()

def get_memory_service(db: Session = Depends(get_db)):
    return MemoryService(db)

@router.get("/memories", response_model=list[MemorySchema])
def get_memories(memory_service: MemoryService = Depends(get_memory_service)):
    return memory_service.get_all_memories()

@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: str, memory_service: MemoryService = Depends(get_memory_service)):
    success = memory_service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "success", "message": "Memory deleted"}
