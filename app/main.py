from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List, Optional
import torch
from tempfile import NamedTemporaryFile
from transformers import pipeline
import time

import os

# Import routers
from app.routers import voice

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(
    title="Vicobi AI API",
    description="API for audio transcription and processing",
    version="1.0.0"
)

# Include routers
app.include_router(voice.router)

# ========== PhoWhisper ASR helper (HuggingFace) - Vietnamese only ==========
_ASR_PIPELINE = None

def get_phowhisper_pipeline(model_name: str = "vinai/PhoWhisper-small", device: int | str | None = None):
    """Initialize and return PhoWhisper pipeline with optimizations"""
    global _ASR_PIPELINE
    if _ASR_PIPELINE is None:
        # device resolution: prefer cuda if available
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
        
        print(f"Loading PhoWhisper model on device {device}...")
        # Enable optimizations
        _ASR_PIPELINE = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=device,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            model_kwargs={"use_safetensors": True} if torch.cuda.is_available() else {}
        )
        print("PhoWhisper model loaded successfully!")
    return _ASR_PIPELINE

def transcribe_with_phowhisper(
    path: str, 
    model_name: str = "vinai/PhoWhisper-small", 
    device: int | str | None = None,
    chunk_length_s: int = 30,
    batch_size: int = 8
) -> str:
    """
    Transcribe an audio file using PhoWhisper (Vietnamese optimized).
    
    Performance optimizations:
    - chunk_length_s: Process audio in chunks for long files
    - batch_size: Process multiple chunks in parallel
    """
    pipe = get_phowhisper_pipeline(model_name=model_name, device=device)
    
    # Optimize for faster inference
    result = pipe(
        path,
        chunk_length_s=chunk_length_s,
        batch_size=batch_size,
        return_timestamps=False  # Disable timestamps for faster processing
    )
    
    # pipeline returns dict with 'text' key
    if isinstance(result, dict):
        return result.get("text", "").strip()
    return ""

# ========== API Endpoints ==========

@app.post("/api/whisper/transcribe")
async def phowhisper_transcribe(
    files: List[UploadFile] = File(...),
    chunk_length_s: int = 30,
    batch_size: int = 8
):
    """
    Transcribe audio files using PhoWhisper model (Vietnamese only).
    
    Args:
        files: Audio files to transcribe (supports multiple)
        chunk_length_s: Length of audio chunks in seconds (default: 30)
                    -largeer chunks = lower memory, but might be slower
        batch_size: Number of chunks to process in parallel (default: 8)
                   Higher batch = faster but more memory usage
    
    Performance tips:
    - Increase batch_size for faster processing (requires more GPU memory)
    - Adjust chunk_length_s based on audio length
    - GPU acceleration automatically enabled if available
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    results = []
    total_start_time = time.time()
    
    for file in files:
        file_start_time = time.time()
        
        suffix = os.path.splitext(file.filename or ".wav")[1] or ".wav"
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp: 
            temp.write(await file.read())
            temp.flush()
            temp_path = temp.name
        
        try:
            transcribe_start_time = time.time()
            text = transcribe_with_phowhisper(
                temp_path,
                chunk_length_s=chunk_length_s,
                batch_size=batch_size
            )
            transcribe_time = time.time() - transcribe_start_time
            file_processing_time = time.time() - file_start_time
            
            results.append({
                "filename": file.filename,
                "transcript": text,
                "model": "vinai/PhoWhisper-small",
                "language": "vi",
                "chunk_length_s": chunk_length_s,
                "batch_size": batch_size,
                "processing_time_seconds": round(file_processing_time, 3),
                "transcription_time_seconds": round(transcribe_time, 3)
            })
        except Exception as e:
            file_processing_time = time.time() - file_start_time
            results.append({
                "filename": file.filename,
                "error": str(e),
                "model": "vinai/PhoWhisper-small",
                "processing_time_seconds": round(file_processing_time, 3)
            })
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    total_processing_time = time.time() - total_start_time
    
    return JSONResponse(content={
        "results": results,
        "total_files": len(files),
        "total_processing_time_seconds": round(total_processing_time, 3)
    })

@app.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    """Redirect root to API documentation"""
    return "/docs"