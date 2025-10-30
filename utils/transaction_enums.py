from enum import Enum


class TransactionType(str, Enum):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'
    REFUND = 'refund'


class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "credit card"
    BANK_TRANSFER = "bank transfer"
    CASH = "cash"
    UPI = "upi"


class AccountEnum(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"
    INVESTMENT = "investment"
