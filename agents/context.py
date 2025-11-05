# agents/context.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDetails:
    """User context information to be passed to agents and tools"""
    user_id: str
    user_name: str
    email: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create UserDetails from dictionary"""
        return cls(
            user_id=data.get("user_id"),
            user_name=data.get("user_name"),
            email=data.get("email")
        )