from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config import settings
from app.database import lifespan as db_lifespan
from app.routers import voice, bill
from app.services.gemini_extractor.gemini_service import get_gemini_service
from app.services.gemini_extractor.config import load_config as load_gemini_config
from app.services.bedrock_extractor.service import get_bedrock_service
from app.services.voice_service import VoiceService
from app.services.bill_service import BillService

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for voice transcription and bill/invoice processing using AI (Gemini + Bedrock)",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=db_lifespan,
    debug=settings.DEBUG,
)

try:
    logger.info("🚀 Initializing AI Services...")
    gemini_config = load_gemini_config()
    gemini_service = get_gemini_service(gemini_config)
    logger.success("✅ Gemini Service initialized")
    bedrock_service = get_bedrock_service()
    logger.success("✅ Bedrock Service initialized")
    voice_business_service = VoiceService(
        gemini_extractor=gemini_service.voice_extractor,
        bedrock_extractor=bedrock_service.voice_extractor
    )
    bill_business_service = BillService(
        gemini_extractor=gemini_service.bill_extractor,
        bedrock_extractor=bedrock_service.bill_extractor
    )
    bill.gemini_service = gemini_service
    bill.bedrock_service = bedrock_service
    voice.voice_service = voice_business_service 
    bill.bill_service = bill_business_service

except Exception as e:
    logger.error(f"❌ Failed to initialize AI Services: {e}")
    bill.gemini_service = None
    voice.voice_service = None

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
    Kiểm tra trạng thái hệ thống và các kết nối AI
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_status": {
            "gemini": "connected" if gemini_service and gemini_service.is_ready() else "disconnected",
            "bedrock": "connected" if bedrock_service and bedrock_service.is_ready() else "disconnected"
        }
    }