from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.auth import verify_jwt
from app.config import settings
from app.database import is_mongodb_connected
from app.schemas.bill import BillResponse
from app.services.bill_service import BillService
from app.services.gemini_extractor.gemini_service import GeminiService, get_gemini_service

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],
)

gemini_service: Optional[GeminiService] = None
bill_service: Optional[BillService] = None

try:
    gemini_service = get_gemini_service()
    if gemini_service:
        bill_service = BillService(gemini_service.bill_extractor)
except Exception:
    pass

@router.get("/health")
async def health_check(user=Depends(verify_jwt)):
    """Kiểm tra trạng thái hoạt động của service"""
    return {
        "status": "healthy",
        "gemini_service": gemini_service is not None and gemini_service.is_ready(),
        "bill_service": bill_service is not None,
        "mongodb": is_mongodb_connected()
    }

@router.post("/extract", response_model=BillResponse)
async def extract_invoice(file: UploadFile = File(...), user=Depends(verify_jwt)):  
    """Trích xuất dữ liệu hóa đơn từ file hình ảnh"""
    if bill_service is None:
        raise HTTPException(
            status_code=503,
            detail="Bill Service chưa được khởi tạo. Kiểm tra lại server logs."
        )
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")   
    
    return await bill_service.process_bill_file(file, cog_sub)