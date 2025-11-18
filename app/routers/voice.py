from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas.voice import VoiceCreateRequest, VoiceResponse
from app.utils import convert_audio_to_wav
from app.services.voice_service import transcribe_audio_file
import os
import tempfile
from pathlib import Path

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

@router.post("/process", response_model=VoiceResponse)
async def process_voice(request: VoiceCreateRequest):
    return {"message": "Voice processing endpoint"}

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Upload file âm thanh (mp3, aac, m4a, mp2, ogg, flac, wav...) và chuyển đổi thành text
    
    Args:
        file: File âm thanh upload
        
    Returns:
        JSON với transcription text và metadata
    """
    temp_input_path = None
    wav_path = None
    
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Tên file không hợp lệ")
        
        # Validate content type (optional, có thể bỏ nếu muốn chấp nhận mọi file)
        allowed_extensions = {'.mp3', '.aac', '.m4a', '.mp2', '.ogg', '.flac', '.wav', '.wma', '.opus'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File format không được hỗ trợ. Các format được chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        # Lưu file upload tạm thời
        temp_dir = tempfile.gettempdir()
        temp_input_path = os.path.join(temp_dir, f"input_{file.filename}")
        
        with open(temp_input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Chuyển đổi sang .wav với config phù hợp cho speech recognition
        wav_path = convert_audio_to_wav(
            input_file=temp_input_path,
            sample_rate=16000,  # PhoWhisper hoạt động tốt với 16kHz
            channels=1  # Mono cho speech recognition
        )
        
        # Chạy transcription
        transcription_result = transcribe_audio_file(wav_path)
        transcription_text = transcription_result.get("text", "")
        model_name = transcription_result.get("model", "unknown")
        
        # Cleanup files
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as cleanup_error:
            print(f"Warning: Không thể xóa file tạm: {cleanup_error}")
        
        return {
            "success": True,
            "transcription": transcription_text,
            "original_filename": file.filename,
            "file_format": file_ext,
            "model": model_name
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File không tồn tại: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file âm thanh: {str(e)}")
    finally:
        # Ensure cleanup even if error occurs
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass

@router.get("/health-check")
async def health_check():
    return {"status": "healthy"}