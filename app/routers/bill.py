from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from app.auth import verify_jwt
from app.config import settings
from app.services.gemini_extractor.gemini_service import GeminiService

gemini_service: Optional[GeminiService] = None
 
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],
)

def validate_image_file(file: UploadFile, user=Depends(verify_jwt)):
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    filename = file.filename or ""
    
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    max_size = 10 * 1024 * 1024
    file.file.seek(0, 2) 
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {max_size / 1024 / 1024}MB"
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.post("/extract")
async def extract_invoice():
    return {"message": "Extraction endpoint placeholder"}