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
    bedrock_ready = service.bedrock_extractor is not None
    mongo_ready = is_mongodb_connected()

    status = "healthy" if bedrock_ready and mongo_ready else "degraded"

    return {
        "status": status,
        "providers": {
            "bedrock": "connected" if bedrock_ready else "not_configured",
        },
        "mongodb": "connected" if mongo_ready else "disconnected"
    }

# @router.post("/process/gemini", response_model=VoiceResponse)
# async def process_audio_gemini(
#     file: UploadFile = File(...), 
#     user=Depends(verify_jwt),
#     service: VoiceService = Depends(get_voice_service)
# ):
#     """
#     Xử lý file audio và trích xuất dữ liệu bằng [Google Gemini]
#     """
#     cog_sub = user.get("sub")
#     if not cog_sub:
#         raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
#     return await service.process_via_gemini(file, cog_sub)

@router.post("/process", response_model=VoiceResponse)
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