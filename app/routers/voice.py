from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.auth import verify_jwt
from app.config import settings
from app.schemas.voice import VoiceResponse
from app.database import is_mongodb_connected
from app.services.gemini_extractor.gemini_service import get_gemini_service, GeminiService
from app.services.voice_service import VoiceService
from app.models.voice import Voice
from typing import Optional, List

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
async def health_check(user=Depends(verify_jwt)):
    """Kiểm tra trạng thái hoạt động của service"""
    return {
        "status": "healthy",
        "gemini_service": gemini_service is not None and gemini_service.is_ready(),
        "voice_service": voice_service is not None,
        "mongodb": is_mongodb_connected()
    }

@router.post("/process", response_model=VoiceResponse)
async def process_audio(file: UploadFile = File(...), user=Depends(verify_jwt)):
    """Xử lý file audio với transcription và trích xuất dữ liệu theo schema"""
    if voice_service is None:
        raise HTTPException(
            status_code=503,
            detail="Voice Service not initialized. Check server logs."
        )
    
    cog_sub = user.get("sub")  # Get cognito sub from JWT
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    
    return await voice_service.process_audio_file(file, cog_sub)
    
@router.get("", response_model=List[VoiceResponse])
async def list_voices(
    skip: int = 0,
    limit: int = 10,
    user=Depends(verify_jwt)
):
    """Lấy danh sách voice records của user hiện tại với phân trang"""
    try:
        cog_sub = user.get("sub")
        if not cog_sub:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        voices = Voice.objects(cog_sub=cog_sub).skip(skip).limit(limit)
        return [
            VoiceResponse(
                voice_id=voice.voice_id,
                total_amount=voice.total_amount.to_mongo(),
                transactions=voice.transactions.to_mongo(),
                money_type=voice.money_type,
                utc_time=voice.utc_time
            )
            for voice in voices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

