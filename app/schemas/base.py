from pydantic import BaseModel, Field

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
    amount: float = Field(..., ge=0, description="Giá cuối cùng")
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(default=1.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 25000000.0,
                "description": "Mua laptop",
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
                        "amount": 850000.0,
                        "description": "Hóa đơn điện",
                        "quantity": 1.0
                    }
                ]
            }
        }
