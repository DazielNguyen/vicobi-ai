import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import lifespan as db_lifespan
from app.routers import voice, bill
from app.services.gemini_extractor.gemini_service import get_gemini_service, GeminiService
from app.services.gemini_extractor.config import load_config

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
    allow_methods=settings.allowed_methods_list,
    allow_headers=settings.allowed_headers_list,
)

app.include_router(voice.router, prefix=settings.API_PREFIX)
app.include_router(bill.router, prefix=settings.API_PREFIX)

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