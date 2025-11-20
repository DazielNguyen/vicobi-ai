from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas.voice import VoiceResponse
from app.database import is_mongodb_connected
from app.services.gemini_extractor.gemini_service import get_gemini_service, GeminiService
from app.services.voice_service import VoiceService
from typing import Optional

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

gemini_service: Optional[GeminiService] = None
voice_service: Optional[VoiceService] = None

try:
    gemini_service = get_gemini_service()
    if gemini_service:
        voice_service = VoiceService(gemini_service)
except Exception:
    pass

@router.get("/health")
async def health_check():
    """Kiểm tra trạng thái hoạt động của service"""
    return {
        "status": "healthy",
        "gemini_service": gemini_service is not None and gemini_service.is_ready(),
        "voice_service": voice_service is not None,
        "mongodb": is_mongodb_connected()
    }

@router.post("/process", response_model=VoiceResponse)
async def process_audio(file: UploadFile = File(...)):
    """Xử lý file audio với transcription và trích xuất dữ liệu theo schema"""
    if voice_service is None:
        raise HTTPException(
            status_code=503,
            detail="Voice Service not initialized. Check server logs."
        )
    
    return await voice_service.process_audio_file(file)

