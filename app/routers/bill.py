from fastapi import APIRouter
from app.config import settings
from app.schemas.bill import BillCreateRequest, BillResponse

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/bills",
    tags=["bill"],
)

@router.post("/process", response_model=BillResponse)
async def process_bill(request: BillCreateRequest):
    return {"message": "Bill creation endpoint"}

@router.get("/health-check")
async def health_check():
    return {"status": "healthy"}