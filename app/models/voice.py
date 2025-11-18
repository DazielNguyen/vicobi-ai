"""
MongoDB models cho Voice data
"""
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime


class VoiceTransactionDetail(EmbeddedDocument):
    """Embedded document cho chi tiết giao dịch"""
    transaction_type = fields.StringField(required=True, choices=["income", "expense"])
    description = fields.StringField(required=True, max_length=500)
    amount = fields.FloatField(required=True, min_value=0)
    amount_string = fields.StringField(required=True)
    quantity = fields.FloatField(default=1.0, min_value=0)


class VoiceTransactions(EmbeddedDocument):
    """Embedded document cho danh sách giao dịch"""
    incomes = fields.ListField(fields.EmbeddedDocumentField(VoiceTransactionDetail), default=list)
    expenses = fields.ListField(fields.EmbeddedDocumentField(VoiceTransactionDetail), default=list)


class VoiceTotalAmount(EmbeddedDocument):
    """Embedded document cho tổng số tiền"""
    incomes = fields.FloatField(default=0.0, min_value=0)
    expenses = fields.FloatField(default=0.0, min_value=0)


class Voice(Document):
    """
    MongoDB document cho Voice data
    Lưu trữ dữ liệu đã xử lý từ transcription
    """
    voice_id = fields.StringField(required=True, unique=True, max_length=100)
    total_amount = fields.EmbeddedDocumentField(VoiceTotalAmount, required=True)
    transactions = fields.EmbeddedDocumentField(VoiceTransactions, required=True)
    money_type = fields.StringField(required=True, choices=["VND", "USD", "EUR"], default="VND")
    utc_time = fields.DateTimeField(default=datetime.utcnow)
    
    # Metadata
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Lưu raw transcription text để tham khảo
    raw_transcription = fields.StringField()
    
    meta = {
        'collection': 'voices',
        'indexes': [
            'voice_id',
            'utc_time',
            'created_at',
            '-created_at',  # Descending index for latest first
        ],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        """Override save để tự động update updated_at"""
        self.updated_at = datetime.utcnow()
        return super(Voice, self).save(*args, **kwargs)
    
    def to_dict(self):
        """Convert to dict for API response"""
        return {
            "voice_id": self.voice_id,
            "total_amount": {
                "incomes": self.total_amount.incomes,
                "expenses": self.total_amount.expenses
            },
            "transactions": {
                "incomes": [
                    {
                        "transaction_type": t.transaction_type,
                        "description": t.description,
                        "amount": t.amount,
                        "amount_string": t.amount_string,
                        "quantity": t.quantity
                    }
                    for t in self.transactions.incomes
                ],
                "expenses": [
                    {
                        "transaction_type": t.transaction_type,
                        "description": t.description,
                        "amount": t.amount,
                        "amount_string": t.amount_string,
                        "quantity": t.quantity
                    }
                    for t in self.transactions.expenses
                ]
            },
            "money_type": self.money_type,
            "utc_time": self.utc_time.isoformat() if self.utc_time else None
        }
