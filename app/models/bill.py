from datetime import datetime, timezone
from typing import List, Optional
from mongoengine import Document, StringField, FloatField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField
from pydantic import BaseModel, Field
from app.models.enum import EnumTransactionTypeField, EnumMoneyTypeField


# ============================================================================
# PYDANTIC MODELS (for Gemini Invoice Extraction)
# ============================================================================

class ProductInfo(BaseModel):
    """Product information from invoice"""
    PRODUCT: str = Field(..., description="Product name")
    NUM: int = Field(..., description="Quantity")
    VALUE: float = Field(..., description="Total value")


class InvoiceData(BaseModel):
    """Invoice data model from Gemini extraction"""
    SELLER: str = Field(..., description="Seller name")
    TIMESTAMP: str = Field(..., description="Transaction timestamp")
    PRODUCTS: List[ProductInfo] = Field(..., description="List of products")
    TOTAL_COST: float = Field(..., description="Total cost")
    ADDRESS: Optional[str] = Field(None, description="Seller address")
    TAX_CODE: Optional[str] = Field(None, description="Tax code")


# ============================================================================
# MONGOENGINE MODELS (for Bill Management)
# ============================================================================

class BillTransactionDetailsField(EmbeddedDocument):
    transaction_type = StringField(required=True, choices=[e.value for e in EnumTransactionTypeField])
    description = StringField(required=True)
    amount = FloatField(required=True, min_value=0)
    discount = FloatField(required=False, min_value=0, default=0)
    amount_after_discount = FloatField(required=True, min_value=0)
    amount_string_after_discount = StringField(required=True)
    quantity = FloatField(required=True, min_value=0, default=1)

class BillTotalAmountField(EmbeddedDocument):
    expenses = FloatField(required=True, default=0, min_value=0)

class BillTransactionField(EmbeddedDocument):
    expenses = ListField(EmbeddedDocumentField(BillTransactionDetailsField), default=list)

class Bill(Document):
    meta = {'collection': 'Bills'}
    bill_id = StringField(required=True, unique=True)
    total_amount = EmbeddedDocumentField(BillTotalAmountField, required=True)
    transactions = EmbeddedDocumentField(BillTransactionField, default=BillTransactionField)
    money_type = StringField(required=True, choices=[e.value for e in EnumMoneyTypeField], default=EnumMoneyTypeField.VND.value)
    utc_time = DateTimeField(default=lambda: datetime.now(timezone.utc))
