from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import lifespan as db_lifespan
from app.routers import voice, bill
from app.services.gemini_extractor.gemini_service import get_gemini_service
from app.services.gemini_extractor.config import load_config
from app.auth import verify_jwt

try:
    config = load_config()
    gemini_service = get_gemini_service(config)
    bill.gemini_service = gemini_service
except Exception as e:
    bill.gemini_service = None

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for voice transcription and bill/invoice processing using AI",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=db_lifespan,
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
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }