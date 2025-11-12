from enum import Enum

class EnumTransactionTypeField(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class EnumMoneyTypeField(Enum):
    VND = "VND"
    USD = "USD"
    EUR = "EUR"