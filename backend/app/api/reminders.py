from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parent import Parent
from app.models.child import Child
from app.models.assignment import Assignment
from app.models.reminder_log import ReminderLog
from app.schemas.reminder import ReminderLogResponse
from app.services.auth import get_current_parent

router = APIRouter(prefix="/api/reminders", tags=["提醒记录"])


@router.get("", response_model=list[ReminderLogResponse])
async def list_reminders(
    parent: Parent = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReminderLog)
        .join(Assignment, ReminderLog.assignment_id == Assignment.id)
        .where(Assignment.parent_id == parent.id)
        .order_by(ReminderLog.sent_at.desc())
    )
    logs = result.scalars().all()

    response = []
    for log in logs:
        assignment_result = await db.execute(
            select(Assignment).where(Assignment.id == log.assignment_id)
        )
        assignment = assignment_result.scalar_one_or_none()
        child_name = None
        assignment_title = None
        if assignment:
            assignment_title = assignment.title
            child_result = await db.execute(select(Child).where(Child.id == assignment.child_id))
            child = child_result.scalar_one_or_none()
            child_name = child.name if child else None

        resp = ReminderLogResponse.model_validate(log)
        resp.assignment_title = assignment_title
        resp.child_name = child_name
        response.append(resp)
    return response
