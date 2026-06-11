"""Tests for assignments management API endpoints."""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


async def create_assignment(client: AsyncClient, auth_headers: dict, child_id: int, **overrides):
    """Helper to create an assignment with sensible defaults."""
    defaults = {
        "child_id": child_id,
        "title": "数学练习册第5页",
        "description": "完成第5-8题",
        "remind_at": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    }
    defaults.update(overrides)
    return await client.post("/api/assignments", json=defaults, headers=auth_headers)


class TestListAssignments:
    """Tests for GET /api/assignments"""

    @pytest.mark.asyncio
    async def test_list_assignments_empty(self, client: AsyncClient, auth_headers: dict):
        """Listing assignments when none exist should return empty list."""
        response = await client.get("/api/assignments", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_assignments_after_create(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Listing assignments after creating one should return the assignment."""
        await create_assignment(client, auth_headers, child_id)

        response = await client.get("/api/assignments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "数学练习册第5页"
        assert data[0]["child_name"] == "小明"
        assert data[0]["status"] == "pending"


class TestCreateAssignment:
    """Tests for POST /api/assignments"""

    @pytest.mark.asyncio
    async def test_create_assignment_success(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Creating an assignment with valid data should succeed."""
        response = await create_assignment(client, auth_headers, child_id)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "数学练习册第5页"
        assert data["description"] == "完成第5-8题"
        assert data["status"] == "pending"
        assert data["child_id"] == child_id
        assert data["child_name"] == "小明"

    @pytest.mark.asyncio
    async def test_create_assignment_without_description(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Creating an assignment without description should succeed (optional)."""
        response = await create_assignment(client, auth_headers, child_id, description="")
        assert response.status_code == 201
        assert response.json()["description"] == ""

    @pytest.mark.asyncio
    async def test_create_assignment_missing_title(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Creating an assignment without title should fail validation."""
        response = await client.post("/api/assignments", json={
            "child_id": child_id,
            "remind_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_assignment_missing_remind_at(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Creating an assignment without remind_at should fail validation."""
        response = await client.post("/api/assignments", json={
            "child_id": child_id,
            "title": "没有时间的作业",
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_assignment_nonexistent_child(self, client: AsyncClient, auth_headers: dict):
        """Creating an assignment for a non-existent child should fail."""
        response = await create_assignment(client, auth_headers, child_id=9999)
        assert response.status_code == 404
        assert "孩子不存在" in response.json()["detail"]


class TestDeleteAssignment:
    """Tests for DELETE /api/assignments/{assignment_id}"""

    @pytest.mark.asyncio
    async def test_delete_assignment_success(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Deleting an existing assignment should succeed."""
        create_resp = await create_assignment(client, auth_headers, child_id)
        assignment_id = create_resp.json()["id"]

        response = await client.delete(f"/api/assignments/{assignment_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify assignment is gone
        list_response = await client.get("/api/assignments", headers=auth_headers)
        assert len(list_response.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_assignment(self, client: AsyncClient, auth_headers: dict):
        """Deleting a non-existent assignment should return 404."""
        response = await client.delete("/api/assignments/9999", headers=auth_headers)
        assert response.status_code == 404
