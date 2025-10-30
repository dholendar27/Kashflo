from datetime import datetime, timezone

from sqlalchemy import Column, String, UUID, DateTime, Boolean
from uuid import uuid4

from sqlalchemy.orm import relationship

from utils import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String(60), unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    categories = relationship('Category', back_populates='user', cascade='all, delete-orphan')
