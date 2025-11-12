"""
Voice schemas for API requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, Optional
from .base import VoiceTotalAmountSchema, VoiceTransactionsSchema


class VoiceCreateRequest(BaseModel):
    """Schema để tạo Voice mới từ frontend"""
    voice_id: str = Field(..., min_length=1, max_length=100)
    total_amount: VoiceTotalAmountSchema
    transactions: VoiceTransactionsSchema
    money_type: Literal["VND", "USD", "EUR"] = "VND"

    model_config = ConfigDict(
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
                            "transaction_type": "income",
                            "description": "Lương tháng 11",
                            "amount": 3000000.0,
                            "amount_string": "3 triệu",
                            "quantity": 1.0
                        }
                    ],
                    "expenses": [
                        {
                            "transaction_type": "expense",
                            "description": "Tiền thuê nhà",
                            "amount": 2000000.0,
                            "amount_string": "2 triệu",
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND"
            }
        }
    )


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
                            "transaction_type": "income",
                            "description": "Lương tháng 11",
                            "amount": 3000000.0,
                            "amount_string": "3 triệu",
                            "quantity": 1.0
                        }
                    ],
                    "expenses": [
                        {
                            "transaction_type": "expense",
                            "description": "Tiền thuê nhà",
                            "amount": 2000000.0,
                            "amount_string": "2 triệu",
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND",
                "utc_time": "2025-11-12T10:30:00.000Z"
            }
        }
    )


class VoiceUpdateRequest(BaseModel):
    """Schema để update Voice"""
    total_amount: Optional[VoiceTotalAmountSchema] = None
    transactions: Optional[VoiceTransactionsSchema] = None
    money_type: Optional[Literal["VND", "USD", "EUR"]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_amount": {
                    "incomes": 6000000.0,
                    "expenses": 4000000.0
                }
            }
        }
    )


class VoiceListResponse(BaseModel):
    """Schema response danh sách Voice"""
    total: int
    items: list[VoiceResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 2,
                "items": [
                    {
                        "voice_id": "voice_20251112_001",
                        "total_amount": {
                            "incomes": 5000000.0,
                            "expenses": 3250000.0
                        },
                        "transactions": {
                            "incomes": [],
                            "expenses": []
                        },
                        "money_type": "VND",
                        "utc_time": "2025-11-12T10:30:00.000Z"
                    }
                ]
            }
        }
    )
