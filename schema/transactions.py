from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from utils.transaction_enums import TransactionType, PaymentMethodEnum, AccountEnum


class TransactionCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    transaction_date: datetime
    transaction_type: TransactionType
    payment_method: PaymentMethodEnum
    account: AccountEnum


class TransactionSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    amount: float
    transaction_date: datetime
    transaction_type: TransactionType
    payment_method: PaymentMethodEnum
    account: AccountEnum
    created_at: datetime
    user_id: UUID
    category_id: UUID


class TransactionCreateResponseSchema(BaseModel):
    message: str
    transaction: TransactionSchema
