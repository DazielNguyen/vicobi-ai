"""
Voice Service - Xử lý logic nghiệp vụ cho Voice processing
"""
import os
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from loguru import logger

from app.services.utils import Utils
from app.utils import convert_audio_to_wav
from app.ai_models.voice import transcribe_audio_file
from app.models.voice import Voice, VoiceTransactionDetail, VoiceTransactions, VoiceTotalAmount
from app.database import is_mongodb_connected
from app.services.gemini_extractor.voice import GeminiVoiceExtractor
from app.schemas.voice import VoiceResponse


class VoiceService:
    """Service xử lý voice processing"""
        
    def __init__(self, voice_extractor: GeminiVoiceExtractor):
        self.voice_extractor = voice_extractor

    def transcribe_audio(self, audio_path: str) -> str:
        """Chuyển đổi file âm thanh sang văn bản sử dụng mô hình AI"""
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
        return self.voice_extractor.extract_to_schema(text)
    
    def save_to_database(
        self,
        voice_id: str,
        cog_sub: str,
        schema_result: Dict[str, Any],
        transcription_text: str,
        utc_time: datetime
    ) -> bool:
        """Lưu kết quả trích xuất vào cơ sở dữ liệu"""
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
        """Tạo response trả về cho client"""
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
        Xử lý file âm thanh: validate, transcribe, extract schema, lưu DB, trả về response
        Args:
            file (UploadFile): File âm thanh tải lên
            cog_sub (str): Cognito sub của user
        Returns:
            VoiceResponse: Kết quả xử lý và trích xuất dữ liệu
        """
        temp_input_path = None
        
        try:
            # Validate file
            if not Utils.is_valid_audio_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail="Định dạng file âm thanh không hợp lệ. Vui lòng tải lên file với định dạng: mp3, wav, m4a, flac, aac, ogg."
                )
            
            # Save temp file
            content = await file.read()
            temp_input_path = Utils.save_temp_file(file, content)
            
            # Transcribe audio
            transcription_text = self.transcribe_audio(temp_input_path)
            
            # Extract schema using Gemini
            schema_result = self.extract_schema_from_text(transcription_text)
            
            # Generate voice_id and timestamp
            voice_id = Utils.generate_unique_filename("voice", file.filename).replace(" ", "_")
            utc_time = datetime.now(timezone.utc)
            
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
