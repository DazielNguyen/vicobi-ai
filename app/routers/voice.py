from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.auth import verify_jwt
from app.config import settings
from app.schemas.voice import VoiceResponse
from app.database import is_mongodb_connected
from app.models.voice import Voice
from app.services.voice_service import VoiceService

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

voice_service: Optional[VoiceService] = None

def get_voice_service() -> VoiceService:
    """
    Dependency helper để đảm bảo VoiceService đã được khởi tạo
    """
    if voice_service is None:
        raise HTTPException(
            status_code=503,
            detail="Voice Service chưa được khởi tạo hoặc đang gặp sự cố."
        )
    return voice_service

@router.get("/health")
async def health_check(
    user=Depends(verify_jwt), 
    service: VoiceService = Depends(get_voice_service) # Check service ready
):
    """Kiểm tra trạng thái hoạt động của các service con"""
    
    # Kiểm tra trạng thái của từng extractor trong service tổng
    gemini_ready = service.gemini_extractor is not None
    bedrock_ready = service.bedrock_extractor is not None
    mongo_ready = is_mongodb_connected()

    status = "healthy" if (gemini_ready or bedrock_ready) and mongo_ready else "degraded"

    return {
        "status": status,
        "providers": {
            "gemini": "connected" if gemini_ready else "not_configured",
            "bedrock": "connected" if bedrock_ready else "not_configured",
        },
        "mongodb": "connected" if mongo_ready else "disconnected"
    }

@router.post("/process/gemini", response_model=VoiceResponse)
async def process_audio_gemini(
    file: UploadFile = File(...), 
    user=Depends(verify_jwt),
    service: VoiceService = Depends(get_voice_service)
):
    """
    Xử lý file audio và trích xuất dữ liệu bằng [Google Gemini]
    """
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    return await service.process_via_gemini(file, cog_sub)

@router.post("/process/bedrock", response_model=VoiceResponse)
async def process_audio_bedrock(
    file: UploadFile = File(...), 
    user=Depends(verify_jwt),
    service: VoiceService = Depends(get_voice_service)
):
    """
    Xử lý file audio và trích xuất dữ liệu bằng [AWS Bedrock - Claude 3.5]
    (Khuyên dùng cho môi trường Private/Production)
    """
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    return await service.process_via_bedrock(file, cog_sub)

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
            raise HTTPException(status_code=401, detail="User chưa được xác thực")
        
        # Sắp xếp theo thời gian mới nhất
        voices = Voice.objects(cog_sub=cog_sub).order_by('-utc_time').skip(skip).limit(limit)
        
        return [
            VoiceResponse(
                voice_id=voice.voice_id,
                total_amount=voice.total_amount.to_mongo(),
                transactions=voice.transactions.to_mongo(),
                money_type=voice.money_type,
                utc_time=voice.utc_time,
                processing_time=voice.processing_time,
                tokens_used=voice.tokens_used
            )
            for voice in voices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách voice: {str(e)}")