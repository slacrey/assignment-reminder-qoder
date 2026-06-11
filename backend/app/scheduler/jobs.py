from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.database import async_session
from app.models.assignment import Assignment, AssignmentStatus
from app.models.child import Child
from app.models.reminder_log import ReminderLog, ReminderStatus
from app.services.email import send_reminder_email

scheduler = AsyncIOScheduler()


async def check_and_send_reminders():
    """Check for pending assignments that need reminders and send emails."""
    async with async_session() as db:
        now = datetime.utcnow()
        result = await db.execute(
            select(Assignment).where(
                Assignment.status == AssignmentStatus.pending,
                Assignment.remind_at <= now,
            )
        )
        pending_assignments = result.scalars().all()

        for assignment in pending_assignments:
            # Get child info
            child_result = await db.execute(select(Child).where(Child.id == assignment.child_id))
            child = child_result.scalar_one_or_none()

            if not child or not child.email:
                # Mark as failed if no email
                log = ReminderLog(
                    assignment_id=assignment.id,
                    channel="email",
                    status=ReminderStatus.failed,
                    error_message="孩子邮箱不存在",
                )
                db.add(log)
                assignment.status = AssignmentStatus.sent
                await db.commit()
                continue

            try:
                await send_reminder_email(
                    to_email=child.email,
                    child_name=child.name,
                    assignment_title=assignment.title,
                    description=assignment.description or "",
                )
                log = ReminderLog(
                    assignment_id=assignment.id,
                    channel="email",
                    status=ReminderStatus.success,
                )
            except Exception as e:
                log = ReminderLog(
                    assignment_id=assignment.id,
                    channel="email",
                    status=ReminderStatus.failed,
                    error_message=str(e),
                )

            db.add(log)
            assignment.status = AssignmentStatus.sent
            await db.commit()


def start_scheduler():
    """Start the APScheduler with a 1-minute interval for checking reminders."""
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        minutes=1,
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
