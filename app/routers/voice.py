from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas.voice import VoiceResponse
from app.utils import convert_audio_to_wav
from app.ai_models.voice import transcribe_audio_file
from app.models.voice import Voice, VoiceTransactionDetail, VoiceTransactions, VoiceTotalAmount
from app.database import mongodb_available, is_mongodb_connected
from app.services.gemini_extractor.gemini_service import get_gemini_service, GeminiService
from typing import Optional
import os
import tempfile
from pathlib import Path

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

gemini_service: Optional[GeminiService] = None

try:
    gemini_service = get_gemini_service()
except Exception:
    pass

@router.get("/health")
async def health_check():
    """Kiểm tra trạng thái hoạt động của service"""
    return {
        "status": "healthy",
        "gemini_service": gemini_service is not None and gemini_service.is_ready(),
        "mongodb": is_mongodb_connected()
    }

@router.post("/process", response_model=VoiceResponse)
async def process_audio(file: UploadFile = File(...)):
    """Xử lý file audio với transcription và trích xuất dữ liệu theo schema"""
    if gemini_service is None or not gemini_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not initialized. Using fallback method."
        )
    
    temp_input_path = None
    wav_path = None
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Tên file không hợp lệ")
        
        allowed_extensions = {'.mp3', '.aac', '.m4a', '.mp2', '.ogg', '.flac', '.wav', '.wma', '.opus'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File format không được hỗ trợ. Các format được chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        temp_dir = tempfile.gettempdir()
        temp_input_path = os.path.join(temp_dir, f"input_{file.filename}")
        
        with open(temp_input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        wav_path = convert_audio_to_wav(
            input_file=temp_input_path,
            sample_rate=16000,
            channels=1
        )
        
        transcription_result = transcribe_audio_file(wav_path)
        transcription_text = transcription_result.get("text", "")
        
        if not transcription_text:
            raise HTTPException(status_code=400, detail="Không thể transcribe được nội dung từ file âm thanh")
        
        # Sử dụng Gemini với schema validation
        schema_result = gemini_service.extract_from_text_to_schema(transcription_text)
        
        # Tạo voice_id và utc_time
        from datetime import datetime
        voice_id = f"voice_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        utc_time = datetime.utcnow()
        
        # Lưu vào database nếu có sẵn
        saved_to_db = False
        if mongodb_available:
            try:
                # Chuyển đổi schema objects sang MongoDB documents
                total_amount_doc = VoiceTotalAmount(
                    incomes=schema_result["total_amount"].incomes,
                    expenses=schema_result["total_amount"].expenses
                )
                
                income_transactions = [
                    VoiceTransactionDetail(
                        transaction_type=t.transaction_type,
                        description=t.description,
                        amount=t.amount,
                        amount_string=t.amount_string,
                        quantity=t.quantity
                    ) for t in schema_result["transactions"].incomes
                ]
                expense_transactions = [
                    VoiceTransactionDetail(
                        transaction_type=t.transaction_type,
                        description=t.description,
                        amount=t.amount,
                        amount_string=t.amount_string,
                        quantity=t.quantity
                    ) for t in schema_result["transactions"].expenses
                ]
                
                transactions_doc = VoiceTransactions(
                    incomes=income_transactions,
                    expenses=expense_transactions
                )
                
                voice_doc = Voice(
                    voice_id=voice_id,
                    total_amount=total_amount_doc,
                    transactions=transactions_doc,
                    money_type=schema_result["money_type"],
                    utc_time=utc_time,
                    raw_transcription=transcription_text
                )
                
                voice_doc.save()
                saved_to_db = True
            except Exception:
                pass
        
        # Trả về response với dữ liệu đã được validate theo schema
        response_data = VoiceResponse(
            voice_id=voice_id,
            total_amount=schema_result["total_amount"].model_dump(),
            transactions=schema_result["transactions"].model_dump(),
            money_type=schema_result["money_type"],
            utc_time=utc_time
        )
        
        return response_data
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Schema validation failed: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File không tồn tại: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")
    finally:
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass

