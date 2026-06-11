from pydantic import BaseModel, EmailStr


class ParentRegister(BaseModel):
    username: str
    password: str
    email: EmailStr


class ParentLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
