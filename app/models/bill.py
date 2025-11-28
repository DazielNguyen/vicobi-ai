from dataclasses import fields
from datetime import datetime, timezone
from mongoengine import Document,EmbeddedDocument, fields

class BillTransactionDetail(EmbeddedDocument):
    """Embedded document cho chi tiết giao dịch"""
    amount = fields.FloatField(required=True, min_value=0)
    description = fields.StringField(required=True, max_length=500)
    quantity = fields.FloatField(default=1.0, min_value=0)

class BillTransactions(EmbeddedDocument):
    """Embedded document cho danh sách giao dịch"""
    expenses = fields.ListField(fields.EmbeddedDocumentField(BillTransactionDetail), default=list)

class BillTotalAmount(EmbeddedDocument):
    """Embedded document cho tổng số tiền"""
    expenses = fields.FloatField(default=0.0, min_value=0)

class Bill(Document):
    """
    MongoDB document cho Bill data
    Lưu trữ dữ liệu đã xử lý từ transcription
    """
    bill_id = fields.StringField(required=True, unique=True, max_length=100)
    cog_sub = fields.StringField(required=True, max_length=100)
    total_amount = fields.EmbeddedDocumentField(BillTotalAmount, required=True)
    transactions = fields.EmbeddedDocumentField(BillTransactions, required=True)
    money_type = fields.StringField(required=True, choices=["VND", "USD", "EUR"], default="VND")
    utc_time = fields.DateTimeField(default=datetime.now(timezone.utc))

    created_at = fields.DateTimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DateTimeField(default=datetime.now(timezone.utc))

    processing_time = fields.FloatField(min_value=0)
    tokens_used = fields.IntField(min_value=0)

    meta = {
        'collection': 'bills',
        'indexes': [
            'bill_id',
            'cog_sub',
            'utc_time',
            'created_at',
            '-created_at',
            ('cog_sub', '-created_at'),
        ],
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        """Override save để tự động update updated_at"""
        self.updated_at = datetime.now(timezone.utc)
        return super(Bill, self).save(*args, **kwargs)
    
    def to_dict(self):
        """Chuyển document thành dict để dễ sử dụng"""
        return {
            "voice_id": self.voice_id,
            "cog_sub": self.cog_sub,
            "total_amount": {
                "expenses": self.total_amount.expenses
            },
            "transactions": {
                "expenses": [
                    {
                        "amount": t.amount,
                        "description": t.description,
                        "quantity": t.quantity
                    } for t in self.transactions.expenses
                ]
            },
            "money_type": self.money_type,
            "utc_time": self.utc_time,
            "processing_time": self.processing_time,
            "tokens_used": self.tokens_used
        }