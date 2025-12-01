from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager

from app.config import settings
from app.database import lifespan as db_lifespan
from app.routers import voice, bill
from app.services.bedrock_extractor.service import get_bedrock_service
from app.ai_models.voice import get_transcriber
from app.services.voice_service import VoiceService
from app.services.bill_service import BillService

ai_services_ready = False
bedrock_service = None

@asynccontextmanager
async def main_lifespan(app: FastAPI):
    """
    Lifespan chính: Kết hợp khởi tạo DB và Load Model AI (Heavy Task)
    """
    global ai_services_ready, bedrock_service

    async with db_lifespan(app):
        logger.info("--- STARTUP: Đang khởi tạo các AI Service (Model Download & Load)... ---")
        
        try:
            bedrock_service = get_bedrock_service()
            
            voice_business_service = VoiceService(        
                bedrock_extractor=bedrock_service.voice_extractor
            )

            bill_business_service = BillService(
                bedrock_extractor=bedrock_service.bill_extractor
            )

            bill.bill_service = bill_business_service
            voice.voice_service = voice_business_service 

            print("--- ⏳ Đang tải PhoWhisper Model... ---")
            get_transcriber() 
            print("--- ✅ PhoWhisper Model đã sẵn sàng! ---")
            
            ai_services_ready = True
            logger.success("✅ STARTUP: Toàn bộ AI Service & Model đã sẵn sàng nhận request!")

        except Exception as e:
            logger.error(f"❌ STARTUP FAILED: Lỗi khởi tạo AI Services: {e}")
        
        yield
        
        logger.info("--- SHUTDOWN: Cleaning up... ---")
        ai_services_ready = False

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for voice transcription and bill/invoice processing using AWS Bedrock AI",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=main_lifespan,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(bill.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Kiểm tra trạng thái hệ thống.
    QUAN TRỌNG: Trả về 503 nếu AI Model chưa load xong để Load Balancer không gửi traffic vào.
    """
    if not ai_services_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="System is starting up, loading AI models..."
        )

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_status": {
            "ready": ai_services_ready,
            "bedrock": "connected" if bedrock_service else "disconnected"
        }
    }