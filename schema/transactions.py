from uuid import UUID
from datetime import datetime
from typing import Optional, List

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
    category_id: UUID


class TransactionSchema(BaseModel):
    model_config = {"from_attributes": True}

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


class TransactionResponse(BaseModel):
    page: int
    limit: int
    total_transaction: int
    total_pages: int
    message: str
    transactions: List[TransactionSchema]

    class Config:
        from_attributes = True


class TransactionUpdateSchema(BaseModel):
    model_config = {"from_attributes": True}

    name: str
    description: Optional[str] = None
    amount: float
    transaction_date: datetime
    transaction_type: TransactionType
    payment_method: PaymentMethodEnum
    account: AccountEnum
    category_id: UUID
