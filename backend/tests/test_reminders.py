"""Tests for reminder logs API endpoint."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from tests.test_db import test_async_session as _test_session


class TestListReminders:
    """Tests for GET /api/reminders"""

    @pytest.mark.asyncio
    async def test_list_reminders_empty(self, client: AsyncClient, auth_headers: dict):
        """Listing reminders when none exist should return empty list."""
        response = await client.get("/api/reminders", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []


class TestReminderLogCreation:
    """Tests that reminder logs are created when the scheduler processes assignments."""

    @pytest.mark.asyncio
    async def test_reminder_log_after_scheduler_run(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """After the scheduler processes a past-due assignment, a reminder log should exist."""
        from app.scheduler.jobs import check_and_send_reminders

        # Create an assignment with a past remind_at time (already due)
        past_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        create_resp = await client.post("/api/assignments", json={
            "child_id": child_id,
            "title": "过期作业测试",
            "description": "这个作业已经到提醒时间了",
            "remind_at": past_time,
        }, headers=auth_headers)
        assert create_resp.status_code == 201

        # Run the scheduler check manually, mock DB session + email
        with patch("app.scheduler.jobs.async_session", _test_session), \
             patch("app.scheduler.jobs.send_reminder_email", new_callable=AsyncMock):
            await check_and_send_reminders()

        # Check reminder logs
        response = await client.get("/api/reminders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # The log should reference our assignment
        log = data[0]
        assert log["assignment_title"] == "过期作业测试"
        assert log["child_name"] == "小明"
        assert log["channel"] == "email"
        assert log["status"] == "success"  # Mocked email should succeed

        # Assignment should be marked as sent
        assignments_resp = await client.get("/api/assignments", headers=auth_headers)
        assignments = assignments_resp.json()
        expired_assignments = [a for a in assignments if a["title"] == "过期作业测试"]
        assert len(expired_assignments) == 1
        assert expired_assignments[0]["status"] == "sent"
