"""
Base schemas cho transaction details và amount fields
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class VoiceTransactionDetailSchema(BaseModel):
    """Schema cho chi tiết giao dịch Voice"""
    amount: float = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(default=1.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 3000000.0,
                "description": "Lương tháng 11",
                "quantity": 1.0
            }
        }


class BillTransactionDetailSchema(BaseModel):
    """Schema cho chi tiết giao dịch Bill với discount"""
    transaction_type: Literal["expense"]
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., ge=0, description="Giá gốc")
    discount: float = Field(default=0.0, ge=0, description="Số tiền giảm giá")
    amount_after_discount: float = Field(..., ge=0, description="Giá sau giảm")
    amount_string_after_discount: str
    quantity: float = Field(default=1.0, ge=0)

    @field_validator('amount_after_discount')
    @classmethod
    def validate_discount(cls, v, info):
        """Validate amount_after_discount = amount - discount"""
        if 'amount' in info.data and 'discount' in info.data:
            expected = info.data['amount'] - info.data['discount']
            if abs(v - expected) > 0.01:  # tolerance for floating point
                raise ValueError(f'amount_after_discount must equal amount - discount')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_type": "expense",
                "description": "Mua laptop",
                "amount": 25000000.0,
                "discount": 2500000.0,
                "amount_after_discount": 22500000.0,
                "amount_string_after_discount": "22,5 triệu",
                "quantity": 1.0
            }
        }


class VoiceTotalAmountSchema(BaseModel):
    """Schema cho tổng số tiền Voice"""
    incomes: float = Field(default=0.0, ge=0)
    expenses: float = Field(default=0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "incomes": 5000000.0,
                "expenses": 3250000.0
            }
        }


class BillTotalAmountSchema(BaseModel):
    """Schema cho tổng số tiền Bill"""
    expenses: float = Field(default=0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "expenses": 2750000.0
            }
        }


class VoiceTransactionsSchema(BaseModel):
    """Schema cho danh sách giao dịch Voice"""
    incomes: list[VoiceTransactionDetailSchema] = Field(default_factory=list)
    expenses: list[VoiceTransactionDetailSchema] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "incomes": [
                    {
                        "amount": 3000000.0,
                        "description": "Lương tháng 11",
                        "quantity": 1.0
                    }
                ],
                "expenses": [
                    {
                        "amount": 2000000.0,
                        "description": "Tiền thuê nhà",
                        "quantity": 1.0
                    }
                ]
            }
        }


class BillTransactionsSchema(BaseModel):
    """Schema cho danh sách giao dịch Bill"""
    expenses: list[BillTransactionDetailSchema] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
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
            }
        }
