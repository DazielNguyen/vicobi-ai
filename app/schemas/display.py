"""
Display schemas optimized for frontend rendering
Các schema này được tối ưu để hiển thị trên UI
"""
from pydantic import BaseModel, Field, computed_field, ConfigDict
from datetime import datetime
from typing import Literal


# ============= Voice Display Schemas =============

class VoiceTransactionDisplay(BaseModel):
    """Schema hiển thị transaction cho Voice - tối ưu cho frontend"""
    stt: int = Field(..., description="Số thứ tự")
    type: Literal["income", "expense"]
    description: str
    amount: float
    amount_formatted: str = Field(..., description="Số tiền đã format (VD: '3 triệu')")
    quantity: float
    subtotal: float = Field(..., description="Tổng = amount × quantity")
    subtotal_formatted: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stt": 1,
                "type": "income",
                "description": "Lương tháng 11",
                "amount": 3000000.0,
                "amount_formatted": "3 triệu",
                "quantity": 1.0,
                "subtotal": 3000000.0,
                "subtotal_formatted": "3 triệu"
            }
        }
    )


class VoiceSummaryDisplay(BaseModel):
    """Schema tổng hợp Voice cho dashboard"""
    voice_id: str
    date: datetime
    total_incomes: float
    total_incomes_formatted: str
    total_expenses: float
    total_expenses_formatted: str
    balance: float = Field(..., description="Số dư = thu - chi")
    balance_formatted: str
    money_type: str
    transaction_count: int = Field(..., description="Tổng số giao dịch")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "voice_id": "voice_20251112_001",
                "date": "2025-11-12T10:30:00.000Z",
                "total_incomes": 5000000.0,
                "total_incomes_formatted": "5 triệu",
                "total_expenses": 3250000.0,
                "total_expenses_formatted": "3,25 triệu",
                "balance": 1750000.0,
                "balance_formatted": "1,75 triệu",
                "money_type": "VND",
                "transaction_count": 5
            }
        }
    )


class VoiceDetailDisplay(BaseModel):
    """Schema chi tiết Voice đầy đủ cho trang detail"""
    voice_id: str
    date: datetime
    money_type: str
    
    # Danh sách thu nhập
    incomes: list[VoiceTransactionDisplay]
    total_incomes: float
    total_incomes_formatted: str
    
    # Danh sách chi tiêu
    expenses: list[VoiceTransactionDisplay]
    total_expenses: float
    total_expenses_formatted: str
    
    # Tổng kết
    balance: float
    balance_formatted: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "voice_id": "voice_20251112_001",
                "date": "2025-11-12T10:30:00.000Z",
                "money_type": "VND",
                "incomes": [
                    {
                        "stt": 1,
                        "type": "income",
                        "description": "Lương tháng 11",
                        "amount": 3000000.0,
                        "amount_formatted": "3 triệu",
                        "quantity": 1.0,
                        "subtotal": 3000000.0,
                        "subtotal_formatted": "3 triệu"
                    }
                ],
                "total_incomes": 5000000.0,
                "total_incomes_formatted": "5 triệu",
                "expenses": [
                    {
                        "stt": 1,
                        "type": "expense",
                        "description": "Tiền thuê nhà",
                        "amount": 2000000.0,
                        "amount_formatted": "2 triệu",
                        "quantity": 1.0,
                        "subtotal": 2000000.0,
                        "subtotal_formatted": "2 triệu"
                    }
                ],
                "total_expenses": 3250000.0,
                "total_expenses_formatted": "3,25 triệu",
                "balance": 1750000.0,
                "balance_formatted": "1,75 triệu"
            }
        }
    )


# ============= Bill Display Schemas =============

class BillItemDisplay(BaseModel):
    """Schema hiển thị từng item trong Bill - format bảng hóa đơn"""
    stt: int = Field(..., description="Số thứ tự")
    name: str = Field(..., description="Tên sản phẩm/dịch vụ")
    quantity: float = Field(..., description="Số lượng")
    price: float = Field(..., description="Giá gốc")
    price_formatted: str
    discount: float = Field(..., description="Giảm giá")
    discount_formatted: str
    price_after_discount: float = Field(..., description="Giá sau giảm")
    price_after_discount_formatted: str
    subtotal: float = Field(..., description="Thành tiền = giá sau giảm × số lượng")
    subtotal_formatted: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stt": 1,
                "name": "Mua laptop",
                "quantity": 1.0,
                "price": 25000000.0,
                "price_formatted": "25 triệu",
                "discount": 2500000.0,
                "discount_formatted": "2,5 triệu",
                "price_after_discount": 22500000.0,
                "price_after_discount_formatted": "22,5 triệu",
                "subtotal": 22500000.0,
                "subtotal_formatted": "22,5 triệu"
            }
        }
    )


class BillSummaryDisplay(BaseModel):
    """Schema tổng hợp Bill cho dashboard"""
    bill_id: str
    date: datetime
    total_amount: float
    total_amount_formatted: str
    total_discount: float = Field(..., description="Tổng giảm giá")
    total_discount_formatted: str
    money_type: str
    item_count: int = Field(..., description="Số lượng items")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bill_id": "bill_20251112_001",
                "date": "2025-11-12T15:45:00.000Z",
                "total_amount": 2750000.0,
                "total_amount_formatted": "2,75 triệu",
                "total_discount": 0.0,
                "total_discount_formatted": "0 đồng",
                "money_type": "VND",
                "item_count": 4
            }
        }
    )


class BillDetailDisplay(BaseModel):
    """Schema chi tiết Bill đầy đủ - tối ưu cho hiển thị bảng hóa đơn"""
    bill_id: str
    date: datetime
    money_type: str
    
    # Danh sách items
    items: list[BillItemDisplay]
    
    # Tổng kết
    total_before_discount: float = Field(..., description="Tổng trước giảm giá")
    total_before_discount_formatted: str
    total_discount: float
    total_discount_formatted: str
    total_amount: float = Field(..., description="Tổng thanh toán")
    total_amount_formatted: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bill_id": "bill_20251112_002",
                "date": "2025-11-12T20:15:00.000Z",
                "money_type": "VND",
                "items": [
                    {
                        "stt": 1,
                        "name": "Mua laptop",
                        "quantity": 1.0,
                        "price": 25000000.0,
                        "price_formatted": "25 triệu",
                        "discount": 2500000.0,
                        "discount_formatted": "2,5 triệu",
                        "price_after_discount": 22500000.0,
                        "price_after_discount_formatted": "22,5 triệu",
                        "subtotal": 22500000.0,
                        "subtotal_formatted": "22,5 triệu"
                    }
                ],
                "total_before_discount": 26650000.0,
                "total_before_discount_formatted": "26,65 triệu",
                "total_discount": 2730000.0,
                "total_discount_formatted": "2,73 triệu",
                "total_amount": 23920000.0,
                "total_amount_formatted": "23,92 triệu"
            }
        }
    )


# ============= Stats & Dashboard Schemas =============

class DashboardStatsDisplay(BaseModel):
    """Schema thống kê tổng quan cho dashboard"""
    total_voices: int
    total_bills: int
    total_incomes: float
    total_incomes_formatted: str
    total_expenses: float
    total_expenses_formatted: str
    net_balance: float = Field(..., description="Số dư ròng")
    net_balance_formatted: str
    period: str = Field(..., description="Kỳ thống kê (VD: 'Tháng 11/2025')")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_voices": 15,
                "total_bills": 8,
                "total_incomes": 75000000.0,
                "total_incomes_formatted": "75 triệu",
                "total_expenses": 48750000.0,
                "total_expenses_formatted": "48,75 triệu",
                "net_balance": 26250000.0,
                "net_balance_formatted": "26,25 triệu",
                "period": "Tháng 11/2025"
            }
        }
    )


class TransactionChartData(BaseModel):
    """Schema data cho biểu đồ thu chi"""
    date: str = Field(..., description="Ngày (format: YYYY-MM-DD)")
    incomes: float
    expenses: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-11-12",
                "incomes": 5000000.0,
                "expenses": 3250000.0
            }
        }
    )
