from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse
from app.services.auth import get_current_parent

router = APIRouter(prefix="/api/children", tags=["孩子管理"])


@router.get("", response_model=list[ChildResponse])
async def list_children(
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Child).where(Child.parent_id == parent.id))
    return result.scalars().all()


@router.post("", response_model=ChildResponse, status_code=201)
async def create_child(
    data: ChildCreate,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    child = Child(
        parent_id=parent.id,
        name=data.name,
        qq_number=data.qq_number,
        email=data.email,
    )
    db.add(child)
    await db.commit()
    await db.refresh(child)
    return child


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    data: ChildUpdate,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Child).where(Child.id == child_id, Child.parent_id == parent.id)
    )
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="孩子不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(child, key, value)

    await db.commit()
    await db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=204)
async def delete_child(
    child_id: int,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Child).where(Child.id == child_id, Child.parent_id == parent.id)
    )
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="孩子不存在")

    await db.delete(child)
    await db.commit()
