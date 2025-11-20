import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger

from app.config import settings
from app.schemas.bill import (
    ExtractionResponse, 
    BatchExtractionResponse, 
    HealthResponse,
    JobStatusResponse,
    JobListResponse
)

# These will be set by main.py during startup
extractor = None
batch_processor = None
config = None

# Directory structure
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
TEMP_DIR = Path("temp")

# In-memory job database (không persistent)
jobs_db: Dict[str, Dict[str, Any]] = {}

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_image_file(file: UploadFile):
    """Validate uploaded image file"""
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    filename = file.filename or ""
    
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
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
    """Save uploaded file to directory"""
    directory.mkdir(exist_ok=True, parents=True)
    file_path = directory / f"{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return file_path


def create_job(total_files: int) -> str:
    """Create new job record"""
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "total_files": total_files,
        "processed": 0,
        "success": 0,
        "failed": 0,
        "results": [],
        "errors": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return job_id


def update_job_progress(job_id: str, result: Dict[str, Any], success: bool):
    """Update job progress"""
    if job_id not in jobs_db:
        return
    
    job = jobs_db[job_id]
    job["processed"] += 1
    
    if success:
        job["success"] += 1
        job["results"].append(result)
    else:
        job["failed"] += 1
        job["errors"].append(result)
    
    if job["processed"] >= job["total_files"]:
        job["status"] = "completed"
    
    job["updated_at"] = datetime.now().isoformat()


async def process_batch_job(
    job_id: str,
    files: List[tuple],
    prompt: str,
    continue_on_error: bool
):
    """Background task to process batch files"""
    for filename, file_path in files:
        try:
            # Extract
            result = extractor.extract(
                image_path=file_path,
                prompt=prompt,
                return_raw=False
            )
            
            # Save result
            output_file = OUTPUT_DIR / f"{job_id}_{filename}.json"
            extractor.save_result(result, output_file)
            
            # Update progress
            update_job_progress(job_id, {
                "filename": filename,
                "data": result,
                "output_file": str(output_file)
            }, success=True)
            
            logger.info(f"✅ Processed {filename} in job {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")
            update_job_progress(job_id, {
                "filename": filename,
                "error": str(e)
            }, success=False)
            
            if not continue_on_error:
                break
        
        finally:
            # Clean up file
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@router.get("/debug")
async def debug_info():
    """Debug endpoint to check initialization status"""
    return {
        "extractor": extractor is not None,
        "batch_processor": batch_processor is not None,
        "config": config is not None,
        "config_api_key_present": bool(config.get('api.api_key')) if config else False,
        "UPLOAD_DIR": str(UPLOAD_DIR),
        "OUTPUT_DIR": str(OUTPUT_DIR),
        "TEMP_DIR": str(TEMP_DIR),
    }


@router.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "extractor_initialized": extractor is not None,
        "config_loaded": config is not None,
        "model_version": config.get('api.model_version') if config else None
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if extractor is not None else "degraded",
        "version": "1.0.0",
        "extractor_initialized": extractor is not None,
        "config_loaded": config is not None,
        "model_version": config.get('api.model_version') if config else None
    }


# ============================================================================
# EXTRACTION ENDPOINTS
# ============================================================================

@router.post("/extract", response_model=ExtractionResponse)
async def extract_invoice(
    file: UploadFile = File(..., description="Invoice image file (JPG, PNG, BMP)"),
    prompt: Optional[str] = Form(default="Extract invoice data to JSON"),
    return_raw: Optional[bool] = Form(default=False),
    save_result: Optional[bool] = Form(default=True)
):
    """
    Single Invoice Extraction
    
    Flow:
    1. Validate file
    2. Save to UPLOAD_DIR
    3. Extract via Gemini API
    4. Save result to OUTPUT_DIR (optional)
    5. Return response
    6. Clean up temp file
    """
    if extractor is None:
        raise HTTPException(
            status_code=503,
            detail="Extractor not initialized. Check server logs."
        )
    
    start_time = datetime.now()
    file_path = None
    
    try:
        # Step 1: Validate
        validate_image_file(file)
        logger.info(f"📁 Processing file: {file.filename}")
        
        # Step 2: Save upload
        file_path = save_upload_file(file, UPLOAD_DIR)
        
        # Step 3: Extract
        result = extractor.extract(
            image_path=file_path,
            prompt=prompt,
            return_raw=return_raw
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        job_id = str(uuid.uuid4())
        
        # Step 4: Save result
        if save_result:
            OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
            output_file = OUTPUT_DIR / f"{job_id}.json"
            extractor.save_result(result, output_file)
        
        logger.info(f"✅ Extraction successful for {file.filename} (job_id: {job_id})")
        
        # Step 5: Return response
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
        logger.error(f"❌ Extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )
    
    finally:
        # Step 6: Clean up
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.debug(f"🧹 Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.post("/extract/batch", response_model=BatchExtractionResponse)
async def extract_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Multiple invoice images"),
    prompt: Optional[str] = Form(default="Extract invoice data to JSON"),
    continue_on_error: Optional[bool] = Form(default=True)
):
    """
    Batch Invoice Extraction
    
    Flow:
    1. Validate & save all files
    2. Create job record
    3. Return job_id immediately
    4. Process files in background
    5. Client polls /jobs/{job_id} for status
    """
    if batch_processor is None:
        raise HTTPException(
            status_code=503,
            detail="Batch processor not initialized"
        )
    
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    # Step 1: Validate & save files
    saved_files = []
    for file in files:
        try:
            validate_image_file(file)
            file_path = save_upload_file(file, UPLOAD_DIR)
            saved_files.append((file.filename, file_path))
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            if not continue_on_error:
                raise HTTPException(status_code=400, detail=str(e))
    
    # Step 2: Create job
    job_id = create_job(len(saved_files))
    
    # Step 3: Add background task
    background_tasks.add_task(
        process_batch_job,
        job_id=job_id,
        files=saved_files,
        prompt=prompt or "Extract invoice data to JSON",
        continue_on_error=continue_on_error if continue_on_error is not None else True
    )
    
    logger.info(f"🚀 Batch job created: {job_id} ({len(saved_files)} files)")
    
    # Step 4: Return immediately
    return {
        "success": True,
        "message": "Batch processing started",
        "job_id": job_id,
        "total_files": len(saved_files),
        "status_url": f"{settings.API_PREFIX}/bills/jobs/{job_id}"
    }


# ============================================================================
# JOB MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and progress"""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return jobs_db[job_id]


@router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """Get detailed job results"""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is still {job['status']}"
        )
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "total_files": job["total_files"],
        "success": job["success"],
        "failed": job["failed"],
        "results": job["results"],
        "errors": job["errors"]
    }


@router.get("/jobs/{job_id}/download")
async def download_job_results(job_id: str):
    """Download all job results as ZIP"""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is still {job['status']}"
        )
    
    # Create ZIP file
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    zip_path = TEMP_DIR / f"{job_id}_results.zip"
    
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for result in job["results"]:
            output_file = Path(result["output_file"])
            if output_file.exists():
                zipf.write(output_file, output_file.name)
    
    return FileResponse(
        path=zip_path,
        filename=f"{job_id}_results.zip",
        media_type="application/zip"
    )


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 100
):
    """List all jobs with optional status filter"""
    jobs = list(jobs_db.values())
    
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    # Sort by created_at desc
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "total": len(jobs),
        "jobs": jobs[:limit]
    }


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job and associated files"""
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_db[job_id]
    
    # Delete output files
    for result in job.get("results", []):
        output_file = Path(result.get("output_file", ""))
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {output_file}: {e}")
    
    # Delete ZIP if exists
    zip_path = TEMP_DIR / f"{job_id}_results.zip"
    if zip_path.exists():
        try:
            zip_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete {zip_path}: {e}")
    
    # Remove from DB
    del jobs_db[job_id]
    
    logger.info(f"🗑️ Deleted job: {job_id}")
    
    return {
        "success": True,
        "message": f"Job {job_id} deleted successfully"
    }
