"""Tests for the scheduler job logic."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.models.parent import Parent
from app.models.child import Child
from app.models.assignment import Assignment, AssignmentStatus
from app.models.reminder_log import ReminderLog, ReminderStatus
from app.services.auth import hash_password
from app.scheduler.jobs import check_and_send_reminders

# We'll use the same test DB from conftest by mocking app.database.async_session
from tests.test_db import test_async_session as _test_session


class TestCheckAndSendReminders:
    """Tests for the check_and_send_reminders scheduler job."""

    @pytest.mark.asyncio
    async def test_sends_email_for_pending_past_due_assignment(self):
        """Scheduler should trigger email for pending assignments past their remind_at time."""
        # Create test data directly
        async with _test_session() as db:
            parent = Parent(
                username="sched_user",
                password_hash=hash_password("test123"),
                email="sched@test.com",
            )
            db.add(parent)
            await db.commit()
            await db.refresh(parent)

            child = Child(
                parent_id=parent.id,
                name="调度测试孩子",
                email="child_sched@test.com",
            )
            db.add(child)
            await db.commit()
            await db.refresh(child)

            assignment = Assignment(
                parent_id=parent.id,
                child_id=child.id,
                title="过期作业",
                description="测试调度器",
                remind_at=datetime.utcnow() - timedelta(minutes=10),
                status=AssignmentStatus.pending,
            )
            db.add(assignment)
            await db.commit()
            await db.refresh(assignment)
            assignment_id = assignment.id

        # Mock the DB session used by scheduler and mock email
        with patch("app.scheduler.jobs.async_session", _test_session), \
             patch("app.scheduler.jobs.send_reminder_email", new_callable=AsyncMock) as mock_send:
            await check_and_send_reminders()
            mock_send.assert_called_once_with(
                to_email="child_sched@test.com",
                child_name="调度测试孩子",
                assignment_title="过期作业",
                description="测试调度器",
            )

        # Verify assignment status updated to 'sent'
        async with _test_session() as db:
            from sqlalchemy import select
            result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
            updated = result.scalar_one()
            assert updated.status == AssignmentStatus.sent

            log_result = await db.execute(select(ReminderLog).where(ReminderLog.assignment_id == assignment_id))
            log = log_result.scalar_one()
            assert log.status == ReminderStatus.success
            assert log.channel == "email"

    @pytest.mark.asyncio
    async def test_skips_future_assignment(self):
        """Scheduler should NOT trigger email for assignments with future remind_at."""
        async with _test_session() as db:
            parent = Parent(
                username="future_user",
                password_hash=hash_password("test123"),
                email="future@test.com",
            )
            db.add(parent)
            await db.commit()
            await db.refresh(parent)

            child = Child(
                parent_id=parent.id,
                name="未来孩子",
                email="future_child@test.com",
            )
            db.add(child)
            await db.commit()
            await db.refresh(child)

            assignment = Assignment(
                parent_id=parent.id,
                child_id=child.id,
                title="未来作业",
                description="还没到时间",
                remind_at=datetime.utcnow() + timedelta(hours=5),
                status=AssignmentStatus.pending,
            )
            db.add(assignment)
            await db.commit()
            await db.refresh(assignment)
            assignment_id = assignment.id

        with patch("app.scheduler.jobs.async_session", _test_session), \
             patch("app.scheduler.jobs.send_reminder_email", new_callable=AsyncMock) as mock_send:
            await check_and_send_reminders()
            mock_send.assert_not_called()

        async with _test_session() as db:
            from sqlalchemy import select
            result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
            updated = result.scalar_one()
            assert updated.status == AssignmentStatus.pending

    @pytest.mark.asyncio
    async def test_skips_already_sent_assignment(self):
        """Scheduler should NOT re-process assignments that are already 'sent'."""
        async with _test_session() as db:
            parent = Parent(
                username="sent_user",
                password_hash=hash_password("test123"),
                email="sent@test.com",
            )
            db.add(parent)
            await db.commit()
            await db.refresh(parent)

            child = Child(
                parent_id=parent.id,
                name="已发孩子",
                email="sent_child@test.com",
            )
            db.add(child)
            await db.commit()
            await db.refresh(child)

            assignment = Assignment(
                parent_id=parent.id,
                child_id=child.id,
                title="已发送作业",
                description="已处理",
                remind_at=datetime.utcnow() - timedelta(hours=1),
                status=AssignmentStatus.sent,
            )
            db.add(assignment)
            await db.commit()

        with patch("app.scheduler.jobs.async_session", _test_session), \
             patch("app.scheduler.jobs.send_reminder_email", new_callable=AsyncMock) as mock_send:
            await check_and_send_reminders()
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_logs_failure_when_email_fails(self):
        """When email sending fails, scheduler should log a failed reminder."""
        async with _test_session() as db:
            parent = Parent(
                username="fail_user",
                password_hash=hash_password("test123"),
                email="fail@test.com",
            )
            db.add(parent)
            await db.commit()
            await db.refresh(parent)

            child = Child(
                parent_id=parent.id,
                name="失败孩子",
                email="fail_child@test.com",
            )
            db.add(child)
            await db.commit()
            await db.refresh(child)

            assignment = Assignment(
                parent_id=parent.id,
                child_id=child.id,
                title="失败作业",
                description="邮件会失败",
                remind_at=datetime.utcnow() - timedelta(minutes=1),
                status=AssignmentStatus.pending,
            )
            db.add(assignment)
            await db.commit()
            await db.refresh(assignment)
            assignment_id = assignment.id

        with patch("app.scheduler.jobs.async_session", _test_session), \
             patch("app.scheduler.jobs.send_reminder_email", new_callable=AsyncMock, side_effect=Exception("SMTP connection failed")):
            await check_and_send_reminders()

        async with _test_session() as db:
            from sqlalchemy import select
            result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
            updated = result.scalar_one()
            assert updated.status == AssignmentStatus.sent

            log_result = await db.execute(select(ReminderLog).where(ReminderLog.assignment_id == assignment_id))
            log = log_result.scalar_one()
            assert log.status == ReminderStatus.failed
            assert "SMTP connection failed" in log.error_message
