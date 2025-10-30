from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID


class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None


class CategorySchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    message: str
    categories: List[CategorySchema]

    class Config:
        from_attributes = True


class CategoryUpdateSchema(BaseModel):
    name: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
