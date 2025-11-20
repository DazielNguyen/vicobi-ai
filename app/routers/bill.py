import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.schemas.bill import ExtractionResponse, HealthResponse
from app.services.gemini_extractor.gemini_service import GeminiService

gemini_service: Optional[GeminiService] = None
 
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],
)

def validate_image_file(file: UploadFile):
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    filename = file.filename or ""
    
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    max_size = 10 * 1024 * 1024  # 10MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {max_size / 1024 / 1024}MB"
        )


def save_upload_file(file: UploadFile, directory: Path = UPLOAD_DIR) -> Path:
    directory.mkdir(exist_ok=True, parents=True)
    file_path = directory / f"{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return file_path

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy" if (gemini_service and gemini_service.is_ready()) else "degraded",
        "version": "1.0.0",
        "extractor_initialized": gemini_service is not None and gemini_service.is_ready(),
        "config_loaded": gemini_service is not None and gemini_service.config is not None,
        "model_version": gemini_service.get_model_version() if gemini_service else None
    }

@router.post("/extract", response_model=ExtractionResponse)
async def extract_invoice(
    file: UploadFile = File(..., description="Invoice image file (JPG, PNG, BMP)")
    ):
    if gemini_service is None or not gemini_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not initialized. Check server logs."
        )
    
    start_time = datetime.now()
    file_path = None
    
    try:
        validate_image_file(file)
        file_path = save_upload_file(file, UPLOAD_DIR)
        result = gemini_service.extract_from_image(
            image_path=file_path,
            return_raw=False
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        job_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "message": "Extraction completed successfully",
            "data": result,
            "job_id": job_id,
            "processing_time": processing_time,
            "metadata": {
                "filename": file.filename,
                "file_size": file_path.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )
    
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

@router.post("/extract-schema", response_model=ExtractionResponse)
async def extract_invoice_to_schema(
    file: UploadFile = File(..., description="Invoice image file (JPG, PNG, BMP)")
    ):
    """Extract invoice data and convert to validated Pydantic schemas"""
    if gemini_service is None or not gemini_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not initialized. Check server logs."
        )
    
    start_time = datetime.now()
    file_path = None
    
    try:
        validate_image_file(file)
        file_path = save_upload_file(file, UPLOAD_DIR)
        
        # Use extract_to_schema instead of extract
        result = gemini_service.extract_from_image_to_schema(
            image_path=file_path
        )
        
        # Convert schema objects to dict for JSON response
        result_dict = {
            "total_amount": result["total_amount"].model_dump(),
            "transactions": result["transactions"].model_dump(),
            "money_type": result["money_type"]
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        job_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "message": "Extraction with schema validation completed successfully",
            "data": result_dict,
            "job_id": job_id,
            "processing_time": processing_time,
            "metadata": {
                "filename": file.filename,
                "file_size": file_path.stat().st_size,
                "timestamp": datetime.now().isoformat(),
                "schema_validated": True
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Schema validation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )
    
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass







