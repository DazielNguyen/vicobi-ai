"""
Bill schemas for API requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, Optional
from .base import BillTransactionDetailSchema, BillTotalAmountSchema, BillTransactionsSchema


class BillCreateRequest(BaseModel):
    """Schema để tạo Bill mới từ frontend"""
    bill_id: str = Field(..., min_length=1, max_length=100)
    total_amount: BillTotalAmountSchema
    transactions: BillTransactionsSchema
    money_type: Literal["VND", "USD", "EUR"] = "VND"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bill_id": "bill_20251112_001",
                "total_amount": {
                    "expenses": 2750000.0
                },
                "transactions": {
                    "expenses": [
                        {
                            "transaction_type": "expense",
                            "description": "Hóa đơn điện",
                            "amount": 850000.0,
                            "discount": 0.0,
                            "amount_after_discount": 850000.0,
                            "amount_string_after_discount": "850 nghìn",
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND"
            }
        }
    )


class BillResponse(BaseModel):
    """Schema response Bill cho frontend"""
    bill_id: str
    total_amount: BillTotalAmountSchema
    transactions: BillTransactionsSchema
    money_type: str
    utc_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "bill_id": "bill_20251112_001",
                "total_amount": {
                    "expenses": 2750000.0
                },
                "transactions": {
                    "expenses": [
                        {
                            "transaction_type": "expense",
                            "description": "Hóa đơn điện",
                            "amount": 850000.0,
                            "discount": 0.0,
                            "amount_after_discount": 850000.0,
                            "amount_string_after_discount": "850 nghìn",
                            "quantity": 1.0
                        }
                    ]
                },
                "money_type": "VND",
                "utc_time": "2025-11-12T15:45:00.000Z"
            }
        }
    )


class BillUpdateRequest(BaseModel):
    """Schema để update Bill"""
    total_amount: Optional[BillTotalAmountSchema] = None
    transactions: Optional[BillTransactionsSchema] = None
    money_type: Optional[Literal["VND", "USD", "EUR"]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_amount": {
                    "expenses": 3000000.0
                }
            }
        }
    )


class BillListResponse(BaseModel):
    """Schema response danh sách Bill"""
    total: int
    items: list[BillResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 2,
                "items": [
                    {
                        "bill_id": "bill_20251112_001",
                        "total_amount": {
                            "expenses": 2750000.0
                        },
                        "transactions": {
                            "expenses": []
                        },
                        "money_type": "VND",
                        "utc_time": "2025-11-12T15:45:00.000Z"
                    }
                ]
            }
        }
    )
