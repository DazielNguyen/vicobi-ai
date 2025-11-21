"""
Voice Service - Xử lý logic nghiệp vụ cho Voice processing
"""
import os
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from loguru import logger

from app.utils import convert_audio_to_wav
from app.ai_models.voice import transcribe_audio_file
from app.models.voice import Voice, VoiceTransactionDetail, VoiceTransactions, VoiceTotalAmount
from app.database import is_mongodb_connected
from app.services.gemini_extractor.gemini_service import GeminiService
from app.schemas.voice import VoiceResponse


class VoiceService:
    """Service xử lý voice processing"""
    
    ALLOWED_EXTENSIONS = {'.mp3', '.aac', '.m4a', '.mp2', '.ogg', '.flac', '.wav', '.wma', '.opus'}
    
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
    
    def validate_audio_file(self, filename: Optional[str]) -> None:
        """Validate audio file format"""
        if not filename:
            raise HTTPException(status_code=400, detail="Tên file không hợp lệ")
        
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File format không được hỗ trợ. Các format được chấp nhận: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
    
    def save_temp_file(self, file: UploadFile, content: bytes) -> str:
        """Save uploaded file to temp directory"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"input_{file.filename}")
        
        with open(temp_path, "wb") as buffer:
            buffer.write(content)
        
        return temp_path
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file to text"""
        wav_path = convert_audio_to_wav(
            input_file=audio_path,
            sample_rate=16000,
            channels=1
        )
        
        transcription_result = transcribe_audio_file(wav_path)
        transcription_text = transcription_result.get("text", "")
        
        # Cleanup wav file
        if os.path.exists(wav_path):
            os.remove(wav_path)
        
        if not transcription_text:
            raise HTTPException(
                status_code=400,
                detail="Không thể transcribe được nội dung từ file âm thanh"
            )
        
        return transcription_text
    
    def extract_schema_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from transcription text using Gemini"""
        return self.gemini_service.extract_from_text_to_schema(text)
    
    def save_to_database(
        self,
        voice_id: str,
        cog_sub: str,
        schema_result: Dict[str, Any],
        transcription_text: str,
        utc_time: datetime
    ) -> bool:
        """Save voice data to MongoDB"""
        if not is_mongodb_connected():
            logger.warning("MongoDB not available, skipping database save")
            return False
        
        try:
            logger.info(f"Attempting to save voice_id={voice_id} to database")
            
            total_amount_doc = VoiceTotalAmount(
                incomes=schema_result["total_amount"].incomes,
                expenses=schema_result["total_amount"].expenses
            )
            
            income_transactions = [
                VoiceTransactionDetail(
                    amount=t.amount,
                    description=t.description,
                    quantity=t.quantity
                ) for t in schema_result["transactions"].incomes
            ]
            
            expense_transactions = [
                VoiceTransactionDetail(
                    amount=t.amount,
                    description=t.description,
                    quantity=t.quantity
                ) for t in schema_result["transactions"].expenses
            ]
            
            transactions_doc = VoiceTransactions(
                incomes=income_transactions,
                expenses=expense_transactions
            )
            
            voice_doc = Voice(
                voice_id=voice_id,
                cog_sub=cog_sub,
                total_amount=total_amount_doc,
                transactions=transactions_doc,
                money_type=schema_result["money_type"],
                utc_time=utc_time,
                raw_transcription=transcription_text,
                processing_time=schema_result.get("processing_time"),
                tokens_used=schema_result.get("tokens_used")
            )
            
            voice_doc.save()
            logger.success(f"✅ Saved voice_id={voice_id} to database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save to database: {e}")
            logger.exception(e)
            return False
    
    def create_response(
        self,
        voice_id: str,
        schema_result: Dict[str, Any],
        utc_time: datetime
    ) -> VoiceResponse:
        """Create VoiceResponse from schema result"""
        return VoiceResponse(
            voice_id=voice_id,
            total_amount=schema_result["total_amount"].model_dump(),
            transactions=schema_result["transactions"].model_dump(),
            money_type=schema_result["money_type"],
            utc_time=utc_time,
            processing_time=schema_result.get("processing_time"),
            tokens_used=schema_result.get("tokens_used")
        )
    
    async def process_audio_file(self, file: UploadFile, cog_sub: str) -> VoiceResponse:
        """
        Process audio file: validate, transcribe, extract, save to DB, and return response
        Main entry point for voice processing workflow
        """
        temp_input_path = None
        
        try:
            # Validate file
            self.validate_audio_file(file.filename)
            
            # Save temp file
            content = await file.read()
            temp_input_path = self.save_temp_file(file, content)
            
            # Transcribe audio
            transcription_text = self.transcribe_audio(temp_input_path)
            
            # Extract schema using Gemini
            schema_result = self.extract_schema_from_text(transcription_text)
            
            # Generate voice_id and timestamp
            voice_id = f"voice_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            utc_time = datetime.utcnow()
            
            # Save to database (best effort)
            self.save_to_database(voice_id, cog_sub, schema_result, transcription_text, utc_time)
            
            # Create and return response
            return self.create_response(voice_id, schema_result, utc_time)
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Schema validation failed: {str(e)}")
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"File không tồn tại: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")
        finally:
            # Cleanup temp file
            if temp_input_path and os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except:
                    pass
