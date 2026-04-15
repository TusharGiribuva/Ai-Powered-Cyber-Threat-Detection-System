from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from schemas.request_models import ChatRequest
from services.chat_service import ask_cyber_ai

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    response = ask_cyber_ai(req.message)
    return {"success": True, "response": response}