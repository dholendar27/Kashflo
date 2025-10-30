from datetime import datetime, timezone
from uuid import uuid4

from utils import Base
from sqlalchemy import Column, String, UUID, DateTime, Boolean


class BlackListToken(Base):
    __tablename__ = "blacklist_tokens"

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    token = Column(String, unique=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    