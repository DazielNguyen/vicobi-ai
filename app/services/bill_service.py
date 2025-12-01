import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, UploadFile
from loguru import logger
from app.models.bill import Bill, BillTotalAmount, BillTransactionDetail, BillTransactions
from app.schemas.bill import BillResponse
from app.services.utils import Utils
from app.ai_models.bill import extract_bill_using_ocr_model, is_bill
from app.database import is_mongodb_connected
from app.services.bedrock_extractor.bill import BedrockBillExtractor


class BillService:
    """Service xử lý Bill processing sử dụng AWS Bedrock AI"""
    
    def __init__(
        self, 
        bedrock_extractor: Optional[BedrockBillExtractor] = None
    ):
        self.bedrock_extractor = bedrock_extractor

    async def process_via_bedrock(self, file: UploadFile, cog_sub: str) -> BillResponse:
        """Xử lý hóa đơn sử dụng AWS Bedrock"""
        if not self.bedrock_extractor:
            raise HTTPException(status_code=503, detail="Bedrock Bill Service chưa được cấu hình")
        
        return await self._process_pipeline(file, cog_sub, self.bedrock_extractor, "bedrock")

    async def _process_pipeline(
        self,
        file: UploadFile,
        cog_sub: str,
        extractor: Union[BedrockBillExtractor],
        provider_name: str
    ) -> BillResponse:
        """
        Luồng xử lý chung: Validate -> Check is_bill -> OCR -> Extract (AI) -> Save DB
        """
        temp_input_path = None
        
        try:
            # 1. Validate Image File
            if not Utils.is_valid_image_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail="Định dạng file không hợp lệ. Hỗ trợ: jpg, jpeg, png, bmp, tiff, gif."
                )

            # 2. Read Content & Check if it is a Bill
            content = await file.read()
            
            # Kiểm tra phân loại ảnh (tránh tốn tiền OCR cho ảnh rác)
            if not is_bill(content):
                raise HTTPException(
                    status_code=400,
                    detail="Hệ thống nhận diện đây không phải là hình ảnh hóa đơn hợp lệ."
                )

            # 3. Save Temp File (OCR model cần đường dẫn file)
            temp_input_path = Utils.save_temp_file(file, content)

            # 4. Perform OCR (Image -> Text/List)
            # Hàm này trả về string hoặc list dict OCR result
            ocr_result = extract_bill_using_ocr_model(temp_input_path)

            # 5. Extract Data to Schema (OCR Result -> JSON Schema)
            schema_result = extractor.extract_to_schema(ocr_result)

            # 6. Generate Metadata
            bill_id = Utils.generate_unique_filename("bill", file.filename).replace(" ", "_")
            bill_id = f"{bill_id}_{provider_name}" # Thêm suffix để track provider
            utc_time = datetime.now(timezone.utc)

            # 7. Save to Database
            # Lưu cả raw OCR result nếu cần (ở đây mình giả sử lưu text đại diện)
            raw_text_for_db = str(ocr_result) if isinstance(ocr_result, list) else ocr_result
            self.save_to_database(bill_id, cog_sub, schema_result, raw_text_for_db, utc_time)

            # 8. Return Response
            return self.create_response(bill_id, schema_result, utc_time)

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Schema validation failed ({provider_name}): {str(e)}")
        except Exception as e:
            logger.error(f"Error in {provider_name} bill pipeline: {e}")
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý hóa đơn: {str(e)}")
        finally:
            # Cleanup temp file
            if temp_input_path and os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except Exception:
                    pass

    def save_to_database(
        self,
        bill_id: str,
        cog_sub: str,
        schema_result: Dict[str, Any],
        raw_text: str, # Thay tên biến cho rõ nghĩa
        utc_time: datetime
    ) -> bool:
        """Lưu dữ liệu hóa đơn vào cơ sở dữ liệu"""

        if not is_mongodb_connected():
            logger.warning("MongoDB not available, skipping database save")
            return False
        
        try:
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
                money_type=schema_result.get("money_type", "VND"), # Đảm bảo có field này
                processing_time=schema_result.get("processing_time"),
                tokens_used=schema_result.get("tokens_used")
                # Nếu model Bill có field raw_text thì lưu raw_text vào đây
            )

            bill_doc.save()
            logger.success(f"✅ Bill {bill_id} saved successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving bill {bill_id}: {str(e)}")
            return False

    def create_response(
        self,
        bill_id: str,
        schema_result: Dict[str, Any],
        utc_time: datetime
    ) -> BillResponse:
        """Tạo response trả về cho client"""
        return BillResponse(
            bill_id=bill_id,
            total_amount=schema_result["total_amount"].model_dump(),
            transactions=schema_result["transactions"].model_dump(),
            money_type=schema_result.get("money_type", "VND"),
            utc_time=utc_time,
            processing_time=schema_result.get("processing_time"),
            tokens_used=schema_result.get("tokens_used")
        )