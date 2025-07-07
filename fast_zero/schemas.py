# fast_zero\schemas.py
from datetime import time

from pydantic import BaseModel, EmailStr, Field


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int = Field(default_factory=lambda: int(time.time()))


class UserPublic(BaseModel):
    id: int = Field(default_factory=lambda: int(time.time()))
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]
