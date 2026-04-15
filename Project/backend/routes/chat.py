from fastapi import APIRouter
from schemas.request_models import ChatRequest
from services.chat_service import ask_cyber_ai

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest):
    response = ask_cyber_ai(req.message)
    return {"success": True, "response": response}