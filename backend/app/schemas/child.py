from pydantic import BaseModel, EmailStr
from datetime import datetime


class ChildCreate(BaseModel):
    name: str
    qq_number: str = ""
    email: EmailStr


class ChildUpdate(BaseModel):
    name: str | None = None
    qq_number: str | None = None
    email: EmailStr | None = None


class ChildResponse(BaseModel):
    id: int
    parent_id: int
    name: str
    qq_number: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
