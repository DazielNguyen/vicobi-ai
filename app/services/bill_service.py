from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from fastapi import HTTPException, UploadFile
from loguru import logger
from app.ai_models.bill import extract_bill_using_ocr_model, is_bill
from app.database import is_mongodb_connected
from app.models.bill import Bill, Bill, BillTotalAmount, BillTransactionDetail, BillTransactions, BillTransactions
from app.schemas.bill import BillResponse
from app.services.gemini_extractor.bill import GeminiBillExtractor
from app.services.utils import Utils    
import time 

class BillService:
    """Service xử lý bill processing"""
    
    def __init__(self, bill_extractor: GeminiBillExtractor):
        self.bill_extractor = bill_extractor

    def extract_bill_using_ocr_model(self, image_path: str) -> dict:
        """Trích xuất dữ liệu hóa đơn từ file hình ảnh từ OCR"""
        return "OCR extraction logic here"
    
    def extract_schema_from_text(self, text: str) -> Dict[str, Any]:
        """Trích xuất schema từ văn bản sử dụng Gemini"""
        return self.bill_extractor.extract_to_schema(text)
    
    def save_to_database(
        self,
        bill_id: str,
        cog_sub: str,
        schema_result: Dict[str, Any],
        transcription_text: str,
        utc_time: datetime
    ) -> bool:
        """Lưu dữ liệu hóa đơn vào cơ sở dữ liệu"""

        if not is_mongodb_connected():
            logger.warning("MongoDB not available, skipping database save")
            return False
        
        try:
            logger.info(f"Saving bill {bill_id} to database for user {cog_sub}")

            total_amount_doc = BillTotalAmount(
                expenses=schema_result["total_amount"].expenses
            )

            expenses_transactions = [
                BillTransactionDetail(
                    amount=t.amount,
                    description=t.description,
                    quantity=t.quantity
                ) for t in schema_result["transactions"].expenses
            ]
            
            transactions_doc = BillTransactions(
                expenses=expenses_transactions
            )

            bill_doc = Bill(
                bill_id=bill_id,
                cog_sub=cog_sub,
                total_amount=total_amount_doc,
                transactions=transactions_doc,
                utc_time=utc_time,
                processing_time=schema_result.get("processing_time"),
                tokens_used=schema_result.get("tokens_used")
            )

            bill_doc.save()
            logger.info(f"Bill {bill_id} saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving bill {bill_id} to database: {str(e)}")
            return False

    
    def create_response(
        self,
        bill_id: str,
        schema_result: Dict[str, Any],
        utc_time: datetime
    ) -> dict:
        """Tạo response trả về cho client"""
        return BillResponse(
            bill_id=bill_id,
            total_amount=schema_result["total_amount"].model_dump(),
            transactions=schema_result["transactions"].model_dump(),
            money_type=schema_result["money_type"],
            utc_time=utc_time,
            processing_time=schema_result.get("processing_time"),
            tokens_used=schema_result.get("tokens_used")
        )

    async def process_bill_file(self, file: UploadFile, cog_sub: str) -> BillResponse:
        """Xử lý file hình ảnh hóa đơn để trích xuất dữ liệu"""

        #Validate image file
        if not Utils.is_valid_image_file(Path(file.filename).name):
            raise HTTPException(
                status_code=400,
                detail="Định dạng file hình ảnh không hợp lệ. Vui lòng tải lên file với định dạng: jpg, jpeg, png, bmp, tiff, gif."
            )

        #Save temp file
        content = await file.read()
        if not is_bill(content):
            raise HTTPException(
                status_code=400,
                detail="File không phải là hóa đơn"
            )
        temp_input_path = Utils.save_temp_file(file, content)

        #Extract bill data
        transcription_text = extract_bill_using_ocr_model(temp_input_path)

        #Extract schema using Gemini
        schema_result = self.bill_extractor.extract_to_schema(transcription_text)

        # Generate voice_id and timestamp
        bill_id = Utils.generate_unique_filename("bill", file.filename).replace(" ", "_")
        utc_time = datetime.now(timezone.utc)

        # Save to database (best effort)
        self.save_to_database(bill_id, cog_sub, schema_result, transcription_text, utc_time)

        #Create and return response
        return self.create_response(bill_id, schema_result, utc_time)