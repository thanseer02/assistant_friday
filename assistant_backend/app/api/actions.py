from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.action_service import ActionPermissionService
from app.services.conversation_service import ConversationService
from app.services.ai_service import AIService
from app.schemas.chat import ChatResponse
from app.api.chat import tool_registry

router = APIRouter()

def get_action_service(db: Session = Depends(get_db)):
    return ActionPermissionService(db)

def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)

def get_ai_service():
    return AIService()

@router.post("/actions/{action_id}/approve", response_model=ChatResponse)
async def approve_action(
    action_id: str,
    action_service: ActionPermissionService = Depends(get_action_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
    ai_service: AIService = Depends(get_ai_service)
):
    action = action_service.get_action(action_id)
    if not action or action.status != "pending":
        raise HTTPException(status_code=404, detail="Pending action not found or already processed")

    # Mark as approved
    action_service.update_action_status(action_id, "approved")

    # Execute the tool safely
    result = await tool_registry.execute_tool(action.tool_name, action.arguments)

    # Note: We need to append the initial tool request and the tool result to the history so AI understands what happened.
    # We append the original tool call as an assistant message
    conversation_service.add_message(action.conversation_id, "assistant", f"I am executing the tool {action.tool_name}.")
    
    # And the result as a tool message
    conversation_service.add_message(action.conversation_id, "tool", result)

    # Continue the conversation loop
    history = conversation_service.get_conversation_history(action.conversation_id)
    response_text = await ai_service.generate_response(history)
    conversation_service.add_message(action.conversation_id, "assistant", response_text)

    return ChatResponse(
        conversation_id=action.conversation_id,
        response=response_text
    )

@router.post("/actions/{action_id}/reject", response_model=ChatResponse)
async def reject_action(
    action_id: str,
    action_service: ActionPermissionService = Depends(get_action_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
    ai_service: AIService = Depends(get_ai_service)
):
    action = action_service.get_action(action_id)
    if not action or action.status != "pending":
        raise HTTPException(status_code=404, detail="Pending action not found or already processed")

    # Mark as rejected
    action_service.update_action_status(action_id, "rejected")

    conversation_service.add_message(action.conversation_id, "assistant", f"I attempted to execute {action.tool_name} but needed permission.")
    conversation_service.add_message(action.conversation_id, "tool", "Error: User rejected the action.")

    history = conversation_service.get_conversation_history(action.conversation_id)
    response_text = await ai_service.generate_response(history)
    conversation_service.add_message(action.conversation_id, "assistant", response_text)

    return ChatResponse(
        conversation_id=action.conversation_id,
        response=response_text
    )
