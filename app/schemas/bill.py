"""
Bill schemas cho response và health check
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.schemas.base import BillTotalAmountSchema, BillTransactionsSchema


class BillResponse(BaseModel):
    """Response trả về dữ liệu hóa đơn đã trích xuất"""
    bill_id: str
    total_amount: BillTotalAmountSchema
    transactions: BillTransactionsSchema
    money_type: str
    utc_time: datetime
    processing_time: Optional[float] = Field(default=None, description="Thời gian xử lý AI (giây)")
    tokens_used: Optional[int] = Field(default=None, description="Số token đã sử dụng")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "bill_id": "bill_20251112_001",
                "total_amount": {
                    "expenses": 3250000.0
                },
                "transactions": {
                    "expenses": [
                        {
                            "description": "Tiền thuê nhà",
                            "amount": 2000000.0,
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND",
                "utc_time": "2025-11-12T10:30:00.000Z",
                "processing_time": 2.45,
                "tokens_used": 1250
            }
        }
    )