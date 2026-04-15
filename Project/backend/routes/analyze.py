from fastapi import APIRouter
from schemas.request_models import AnalyzeRequest
from services.threat_service import analyze_payload

router = APIRouter()

@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = analyze_payload(req.text)
    return {"success": True, "result": result}