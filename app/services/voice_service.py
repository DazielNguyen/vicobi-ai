import os
from datetime import datetime, timezone
from typing import Dict, Any, Union, Optional
from fastapi import UploadFile, HTTPException
from loguru import logger

from app.services.utils import Utils
from app.ai_models.voice import transcribe_audio_file
from app.models.voice import Voice, VoiceTransactionDetail, VoiceTransactions, VoiceTotalAmount
from app.database import is_mongodb_connected
from app.schemas.voice import VoiceResponse

# Import cả 2 Extractors
from app.services.gemini_extractor.voice import GeminiVoiceExtractor
from app.services.bedrock_extractor.voice import BedrockVoiceExtractor


class VoiceService:
    """Service xử lý voice processing hỗ trợ cả Gemini và Bedrock"""
        
    def __init__(
        self, 
        gemini_extractor: Optional[GeminiVoiceExtractor] = None,
        bedrock_extractor: Optional[BedrockVoiceExtractor] = None
    ):
        self.gemini_extractor = gemini_extractor
        self.bedrock_extractor = bedrock_extractor

    def transcribe_audio(self, audio_path: str) -> str:
        """Chuyển đổi file âm thanh sang văn bản (Dùng chung cho cả 2 luồng)"""
        wav_path = Utils.convert_audio_to_wav(
            input_file=audio_path,
            sample_rate=16000,
            channels=1
        )
        
        try:
            transcription_result = transcribe_audio_file(wav_path)
            transcription_text = transcription_result.get("text", "")
            
            if not transcription_text:
                raise HTTPException(
                    status_code=400,
                    detail="Không thể transcribe được nội dung từ file âm thanh"
                )
            return transcription_text
            
        finally:
            # Cleanup wav file converted from pydub
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

    async def process_via_gemini(self, file: UploadFile, cog_sub: str) -> VoiceResponse:
        """
        Xử lý file âm thanh sử dụng Google Gemini để trích xuất dữ liệu
        """
        if not self.gemini_extractor:
            raise HTTPException(status_code=503, detail="Gemini Service chưa được cấu hình")

        return await self._process_pipeline(file, cog_sub, self.gemini_extractor, "gemini")

    async def process_via_bedrock(self, file: UploadFile, cog_sub: str) -> VoiceResponse:
        """
        Xử lý file âm thanh sử dụng AWS Bedrock (Claude 3) để trích xuất dữ liệu
        """
        if not self.bedrock_extractor:
            raise HTTPException(status_code=503, detail="Bedrock Service chưa được cấu hình")

        return await self._process_pipeline(file, cog_sub, self.bedrock_extractor, "bedrock")

    async def _process_pipeline(
        self, 
        file: UploadFile, 
        cog_sub: str, 
        extractor: Union[GeminiVoiceExtractor, BedrockVoiceExtractor],
        provider_name: str
    ) -> VoiceResponse:
        """
        Luồng xử lý chung: Validate -> Save Temp -> Transcribe -> Extract (bằng extractor truyền vào) -> Save DB
        """
        temp_input_path = None
        
        try:
            # 1. Validate file
            if not Utils.is_valid_audio_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail="Định dạng file không hợp lệ. Hỗ trợ: mp3, wav, m4a, flac, aac, ogg."
                )
            
            # 2. Save temp file
            content = await file.read()
            temp_input_path = Utils.save_temp_file(file, content)
            
            # 3. Transcribe audio (Chuyển Audio -> Text)
            # Lưu ý: Bước này dùng model local (Whisper) hoặc API chung, độc lập với Gemini/Bedrock
            transcription_text = self.transcribe_audio(temp_input_path)
            
            # 4. Extract schema (Text -> JSON)
            # Gọi hàm extract_to_schema của extractor được truyền vào (Gemini hoặc Bedrock)
            schema_result = extractor.extract_to_schema(transcription_text)
            print("="*50)
            print(f"🧾 SCHEMA RESULT: {schema_result}")
            print("="*50)
            # 5. Generate Metadata
            voice_id = Utils.generate_unique_filename("voice", file.filename).replace(" ", "_")
            # Thêm suffix provider vào ID để dễ debug (vd: voice_abc_gemini)
            voice_id = f"{voice_id}_{provider_name}" 
            utc_time = datetime.now(timezone.utc)
            
            # 6. Save to database
            self.save_to_database(voice_id, cog_sub, schema_result, transcription_text, utc_time)
            
            # 7. Return Response
            return self.create_response(voice_id, schema_result, utc_time)
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Schema validation failed ({provider_name}): {str(e)}")
        except Exception as e:
            logger.error(f"Error in {provider_name} pipeline: {e}")
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý hệ thống: {str(e)}")
        finally:
            # Cleanup temp input file
            if temp_input_path and os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except Exception:
                    pass

    def save_to_database(
        self,
        voice_id: str,
        cog_sub: str,
        schema_result: Dict[str, Any],
        transcription_text: str,
        utc_time: datetime
    ) -> bool:
        """Lưu kết quả trích xuất vào MongoDB"""
        if not is_mongodb_connected():
            logger.warning("MongoDB not available, skipping database save")
            return False
        
        try:
            total_amount_doc = VoiceTotalAmount(
                incomes=schema_result["total_amount"].incomes,
                expenses=schema_result["total_amount"].expenses
            )
            
            income_transactions = [
                VoiceTransactionDetail(**t.model_dump()) for t in schema_result["transactions"].incomes
            ]
            
            expense_transactions = [
                VoiceTransactionDetail(**t.model_dump()) for t in schema_result["transactions"].expenses
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