from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parent import Parent
from app.schemas.auth import ParentRegister, ParentLogin, Token
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token)
async def register(data: ParentRegister, db: AsyncSession = Depends(get_db)):
    # Check if username exists
    result = await db.execute(select(Parent).where(Parent.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    parent = Parent(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
    )
    db.add(parent)
    await db.commit()
    await db.refresh(parent)

    token = create_access_token({"sub": str(parent.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(data: ParentLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Parent).where(Parent.username == data.username))
    parent = result.scalar_one_or_none()

    if not parent or not verify_password(data.password, parent.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": str(parent.id)})
    return Token(access_token=token)
