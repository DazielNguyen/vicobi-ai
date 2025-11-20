"""
Voice schemas for API responses
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .base import VoiceTotalAmountSchema, VoiceTransactionsSchema


class VoiceResponse(BaseModel):
    """Schema response Voice cho frontend"""
    voice_id: str
    total_amount: VoiceTotalAmountSchema
    transactions: VoiceTransactionsSchema
    money_type: str
    utc_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "voice_id": "voice_20251112_001",
                "total_amount": {
                    "incomes": 5000000.0,
                    "expenses": 3250000.0
                },
                "transactions": {
                    "incomes": [
                        {
                            "description": "Lương tháng 11",
                            "amount": 3000000.0,
                            "quantity": 1.0
                        }
                    ],
                    "expenses": [
                        {
                            "description": "Tiền thuê nhà",
                            "amount": 2000000.0,
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND",
                "utc_time": "2025-11-12T10:30:00.000Z"
            }
        }
    )
