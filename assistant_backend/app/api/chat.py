from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.database.session import get_db

router = APIRouter()

def get_ai_service():
    return AIService()

def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)

def get_memory_service(db: Session = Depends(get_db)):
    return MemoryService(db)

async def background_extract_memories(message: str, ai_service: AIService, memory_service: MemoryService):
    extracted = await ai_service.extract_memories(message)
    for mem in extracted:
        if "key" in mem and "value" in mem:
            memory_service.save_memory(
                key=mem["key"], 
                value=mem["value"], 
                category=mem.get("category", "fact")
            )

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    ai_service: AIService = Depends(get_ai_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
    memory_service: MemoryService = Depends(get_memory_service)
):
    # 1. Get or create conversation
    conversation = conversation_service.get_or_create_conversation(request.conversation_id)
    
    # 2. Save the user message
    conversation_service.add_message(conversation.id, "user", request.message)
    
    # 3. Retrieve conversation history
    history = conversation_service.get_conversation_history(conversation.id)
    
    # 4. Search long-term memories related to the user's message
    memories_db = memory_service.search_memories(request.message)
    memory_strings = [f"{m.key}: {m.value}" for m in memories_db]
    
    # 5. Generate response via AI, injecting memories
    response_text = await ai_service.generate_response(history, memories=memory_strings)
    
    # 6. Save AI response
    conversation_service.add_message(conversation.id, "assistant", response_text)
    
    # 7. Background task: Extract and save new memories from user message
    background_tasks.add_task(background_extract_memories, request.message, ai_service, memory_service)
    
    # 8. Return response
    return ChatResponse(conversation_id=conversation.id, response=response_text)
