from fastapi import APIRouter
from app.config import settings
from app.schemas.voice import VoiceCreateRequest, VoiceResponse

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

@router.post("", response_model=VoiceResponse)
async def process_voice(request: VoiceCreateRequest):
    return {"message": "Voice processing endpoint"}

@router.get("/health-check")
async def health_check():
    return {"status": "healthy"}