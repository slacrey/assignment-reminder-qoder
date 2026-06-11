from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.models.assignment import Assignment, AssignmentStatus
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.services.auth import get_current_parent

router = APIRouter(prefix="/api/assignments", tags=["作业管理"])


@router.get("", response_model=list[AssignmentResponse])
async def list_assignments(
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment)
        .where(Assignment.parent_id == parent.id)
        .order_by(Assignment.remind_at)
    )
    assignments = result.scalars().all()

    response = []
    for a in assignments:
        child_result = await db.execute(select(Child).where(Child.id == a.child_id))
        child = child_result.scalar_one_or_none()
        resp = AssignmentResponse.model_validate(a)
        resp.child_name = child.name if child else "未知"
        response.append(resp)
    return response


@router.post("", response_model=AssignmentResponse, status_code=201)
async def create_assignment(
    data: AssignmentCreate,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    # Verify child belongs to parent
    result = await db.execute(
        select(Child).where(Child.id == data.child_id, Child.parent_id == parent.id)
    )
    child = result.scalar_one_or_none()
    if not child:
        raise HTTPException(status_code=404, detail="孩子不存在")

    assignment = Assignment(
        parent_id=parent.id,
        child_id=data.child_id,
        title=data.title,
        description=data.description,
        remind_at=data.remind_at,
        status=AssignmentStatus.pending,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    resp = AssignmentResponse.model_validate(assignment)
    resp.child_name = child.name
    return resp


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id, Assignment.parent_id == parent.id
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)

    await db.commit()
    await db.refresh(assignment)

    child_result = await db.execute(select(Child).where(Child.id == assignment.child_id))
    child = child_result.scalar_one_or_none()
    resp = AssignmentResponse.model_validate(assignment)
    resp.child_name = child.name if child else "未知"
    return resp


@router.delete("/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: int,
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id, Assignment.parent_id == parent.id
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    await db.delete(assignment)
    await db.commit()
