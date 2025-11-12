from mongoengine import Document, StringField, FloatField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField
from app.models.enum import EnumTransactionTypeField, EnumMoneyTypeField
from datetime import datetime, timezone

class VoiceTransactionDetailsField(EmbeddedDocument):
    transaction_type = StringField(required=True, choices=[e.value for e in EnumTransactionTypeField])
    description = StringField(required=True)
    amount = FloatField(required=True, min_value=0)
    amount_string = StringField(required=True)
    quantity = FloatField(required=True, min_value=0, default=1)

class VoiceTotalAmountField(EmbeddedDocument):
    incomes = FloatField(required=True, default=0, min_value=0)
    expenses = FloatField(required=True, default=0, min_value=0)

class VoiceTransactionField(EmbeddedDocument):
    incomes = ListField(EmbeddedDocumentField(VoiceTransactionDetailsField), default=list)
    expenses = ListField(EmbeddedDocumentField(VoiceTransactionDetailsField), default=list)

class Voice(Document):
    meta = {'collection': 'Voices'}
    voice_id = StringField(required=True, unique=True)
    total_amount = EmbeddedDocumentField(VoiceTotalAmountField, required=True)
    transactions = EmbeddedDocumentField(VoiceTransactionField, default=VoiceTransactionField)
    money_type = StringField(required=True, choices=[e.value for e in EnumMoneyTypeField], default=EnumMoneyTypeField.VND.value)
    utc_time = DateTimeField(default=lambda: datetime.now(timezone.utc))