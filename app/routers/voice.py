from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas.voice import VoiceResponse
from app.utils import convert_audio_to_wav
from app.services.voice_service import transcribe_audio_file, parse_transcription_to_voice_data
from app.models.voice import Voice, VoiceTransactionDetail, VoiceTransactions, VoiceTotalAmount
from app.database import mongodb_available
import os
import tempfile
from pathlib import Path

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/voices",
    tags=["voice"],    
)

@router.post("/process-audio", response_model=VoiceResponse)
async def process_audio_to_voice(file: UploadFile = File(...)):
    """
    Upload file âm thanh → Transcribe → Parse thành structured data → Lưu MongoDB
    
    Flow hoàn chỉnh:
    1. Upload audio (mp3, aac, m4a, mp2, ogg, flac, wav...)
    2. Convert sang .wav
    3. Transcribe sang text
    4. Parse text thành income/expense transactions
    5. Lưu vào MongoDB
    6. Trả về VoiceResponse JSON
    
    Args:
        file: File âm thanh upload
        
    Returns:
        VoiceResponse với structured data
    """
    temp_input_path = None
    wav_path = None
    
    try:
        # 1. Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Tên file không hợp lệ")
        
        allowed_extensions = {'.mp3', '.aac', '.m4a', '.mp2', '.ogg', '.flac', '.wav', '.wma', '.opus'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File format không được hỗ trợ. Các format được chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        # 2. Save uploaded file temporarily
        temp_dir = tempfile.gettempdir()
        temp_input_path = os.path.join(temp_dir, f"input_{file.filename}")
        
        with open(temp_input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 3. Convert to .wav
        wav_path = convert_audio_to_wav(
            input_file=temp_input_path,
            sample_rate=16000,
            channels=1
        )
        
        # 4. Transcribe audio to text
        transcription_result = transcribe_audio_file(wav_path)
        transcription_text = transcription_result.get("text", "")
        
        if not transcription_text:
            raise HTTPException(status_code=400, detail="Không thể transcribe được nội dung từ file âm thanh")
        
        # 5. Parse transcription to structured voice data
        voice_data = parse_transcription_to_voice_data(transcription_text)
        
        # 6. Save to MongoDB (if available)
        saved_to_db = False
        if mongodb_available:
            try:
                # Tạo embedded documents
                total_amount_doc = VoiceTotalAmount(
                    incomes=voice_data["total_amount"]["incomes"],
                    expenses=voice_data["total_amount"]["expenses"]
                )
                
                # Tạo transactions
                income_transactions = [
                    VoiceTransactionDetail(**t) for t in voice_data["transactions"]["incomes"]
                ]
                expense_transactions = [
                    VoiceTransactionDetail(**t) for t in voice_data["transactions"]["expenses"]
                ]
                
                transactions_doc = VoiceTransactions(
                    incomes=income_transactions,
                    expenses=expense_transactions
                )
                
                # Tạo Voice document
                voice_doc = Voice(
                    voice_id=voice_data["voice_id"],
                    total_amount=total_amount_doc,
                    transactions=transactions_doc,
                    money_type=voice_data["money_type"],
                    utc_time=voice_data["utc_time"],
                    raw_transcription=voice_data["raw_transcription"]
                )
                
                # Save to database
                voice_doc.save()
                saved_to_db = True
                print(f"✓ Saved to MongoDB: {voice_data['voice_id']}")
            except Exception as db_error:
                print(f"⚠️  MongoDB save failed: {db_error}")
                # Continue without saving - still return the data
        
        # 7. Cleanup temp files
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as cleanup_error:
            print(f"Warning: Không thể xóa file tạm: {cleanup_error}")
        
        # 8. Return response (from parsed data, not from DB)
        response_data = VoiceResponse(
            voice_id=voice_data["voice_id"],
            total_amount=voice_data["total_amount"],
            transactions=voice_data["transactions"],
            money_type=voice_data["money_type"],
            utc_time=voice_data["utc_time"]
        )
        
        # Add metadata if MongoDB not available
        if not saved_to_db:
            print(f"⚠️  Data NOT saved to MongoDB (connection unavailable)")
        
        return response_data
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File không tồn tại: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")
    finally:
        # Ensure cleanup
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass