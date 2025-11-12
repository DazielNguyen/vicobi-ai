from datetime import datetime, timezone
from mongoengine import Document, StringField, FloatField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField
from app.models.enum import EnumTransactionTypeField, EnumMoneyTypeField

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
