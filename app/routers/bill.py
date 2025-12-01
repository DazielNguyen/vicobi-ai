from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.auth import verify_jwt
from app.config import settings
from app.schemas.bill import BillResponse
from app.database import is_mongodb_connected
from app.services.bill_service import BillService

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],    
)
bill_service: Optional[BillService] = None

def get_bill_service() -> BillService:
    if bill_service is None:
        raise HTTPException(status_code=503, detail="Bill Service chưa được khởi tạo")
    return bill_service

@router.get("/health")
async def health_check(
    user=Depends(verify_jwt),
    service: BillService = Depends(get_bill_service)
):
    """Kiểm tra trạng thái Bill Service"""
    bedrock_ready = service.bedrock_extractor is not None
    mongo_ready = is_mongodb_connected()

    return {
        "status": "healthy" if (bedrock_ready) and mongo_ready else "degraded",
        "providers": {
            "bedrock": "connected" if bedrock_ready else "not_configured"
        },
        "mongodb": "connected" if mongo_ready else "disconnected"
    }

# @router.post("/extract/gemini", response_model=BillResponse)
# async def process_bill_gemini(
#     file: UploadFile = File(...), 
#     user=Depends(verify_jwt),
#     service: BillService = Depends(get_bill_service)
# ):
#     """Xử lý hóa đơn bằng [Google Gemini]"""
#     cog_sub = user.get("sub")
#     if not cog_sub:
#         raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
#     return await service.process_via_gemini(file, cog_sub)

@router.post("/extract", response_model=BillResponse)
async def process_bill_bedrock(
    file: UploadFile = File(...), 
    user=Depends(verify_jwt),
    service: BillService = Depends(get_bill_service)
):
    """Xử lý hóa đơn bằng [AWS Bedrock - Claude 3.5]"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    return await service.process_via_bedrock(file, cog_sub)