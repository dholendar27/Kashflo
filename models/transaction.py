from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, UUID, DateTime, Table, ForeignKey, Float, DECIMAL, Text, Enum
from sqlalchemy.orm import relationship

from utils import Base
from utils.transaction_enums import AccountEnum, TransactionType, PaymentMethodEnum


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

    user_id = Column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='categories')


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID, primary_key=True, default=uuid4, nullable=False)
    transaction_date = Column(DateTime, nullable=False)  # Renamed for clarity
    amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category_id = Column(UUID, ForeignKey('categories.id'))
    user_id = Column(UUID, ForeignKey('users.id'))
    description = Column(Text, nullable=True)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    balance_after = Column(DECIMAL(10, 2), nullable=True)
    account = Column(Enum(AccountEnum), nullable=False)

    user = relationship('User', back_populates='transactions')
    category = relationship('Category', back_populates='transactions')

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
