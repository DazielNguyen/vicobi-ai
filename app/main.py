from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager
from app.config import settings
from app.database import lifespan as db_lifespan
from app.routers import voice, bill, chatbot
from app.services.bedrock_extractor.service import get_bedrock_service
from app.ai_models.voice import get_transcriber
from app.services.voice_service import VoiceService
from app.services.bill_service import BillService
from app.services.chatbot_service import get_chatbot_service_instance

ai_services_ready = False
bedrock_service = None

@asynccontextmanager
async def main_lifespan(app: FastAPI):
    """Application lifespan: Initialize database and load AI models"""
    global ai_services_ready, bedrock_service

    async with db_lifespan(app):        
        try:
            bedrock_service = get_bedrock_service()

            chatbot_business_service = get_chatbot_service_instance(
                bedrock_extractor=bedrock_service.chat_extractor
            )

            voice_business_service = VoiceService(        
                bedrock_extractor=bedrock_service.voice_extractor
            )

            bill_business_service = BillService(
                bedrock_extractor=bedrock_service.bill_extractor
            )

            bill.bill_service = bill_business_service
            voice.voice_service = voice_business_service 
            chatbot.chatbot_service = chatbot_business_service
                        
            logger.info("Loading PhoWhisper model...")
            get_transcriber()
            from app.ai_models.voice import is_transcriber_ready
            if not is_transcriber_ready():
                raise RuntimeError("Failed to load PhoWhisper model")
            
            logger.info("Loading Embedding model for chatbot...")
            from app.ai_models.embeddings import get_embedding_model, is_embedding_model_ready
            get_embedding_model()
            if not is_embedding_model_ready():
                raise RuntimeError("Failed to load Embedding model")
            
            from app.ai_models.bill import is_bill_model_ready
            if not is_bill_model_ready():
                raise RuntimeError("Failed to load Bill classifier model")
            logger.info("Bill classifier and EasyOCR ready")
            
            # Auto-initialize context files từ folder context
            logger.info("Initializing context files...")
            from app.services.context_initializer import auto_initialize_context
            context_result = await auto_initialize_context(chatbot_business_service)
            if context_result.get("files_processed", 0) > 0:
                logger.success(f"Context initialized: {context_result['files_processed']} file(s) embedded")
            elif context_result.get("files_skipped", 0) > 0:
                logger.info(f"Context files already initialized: {context_result['files_skipped']} file(s) skipped")
                        
            ai_services_ready = True
            logger.success("STARTUP: All AI Services and Models are ready")

        except Exception as e:
            logger.error(f"STARTUP FAILED: Error initializing AI Services: {e}")
        
        yield
        
        logger.info("SHUTDOWN: Cleaning up resources...")
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
app.include_router(chatbot.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
async def health_check():
    """Check system status. Returns 503 if AI models are not ready."""
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