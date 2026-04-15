from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from schemas.request_models import AnalyzeRequest
from services.threat_service import analyze_payload

router = APIRouter()

@router.post("/analyze")
def analyze(req: AnalyzeRequest, user=Depends(get_current_user)):
    result = analyze_payload(req.text)
    return {"success": True, "result": result}