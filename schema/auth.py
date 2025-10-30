from pydantic import BaseModel
from uuid import UUID


class UserSignupSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserSignupResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_verified: bool


class UserLoginSchema(BaseModel):
    email: str
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class UserSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_verified: bool
