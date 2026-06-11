"""Tests for children management API endpoints."""
import pytest
from httpx import AsyncClient


class TestListChildren:
    """Tests for GET /api/children"""

    @pytest.mark.asyncio
    async def test_list_children_empty(self, client: AsyncClient, auth_headers: dict):
        """Listing children when none exist should return empty list."""
        response = await client.get("/api/children", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_children_after_create(self, client: AsyncClient, auth_headers: dict):
        """Listing children after creating one should return the child."""
        await client.post("/api/children", json={
            "name": "小红",
            "email": "xiaohong@test.com",
            "qq_number": "111111",
        }, headers=auth_headers)

        response = await client.get("/api/children", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "小红"
        assert data[0]["email"] == "xiaohong@test.com"
        assert data[0]["qq_number"] == "111111"


class TestCreateChild:
    """Tests for POST /api/children"""

    @pytest.mark.asyncio
    async def test_create_child_success(self, client: AsyncClient, auth_headers: dict):
        """Creating a child with valid data should succeed."""
        response = await client.post("/api/children", json={
            "name": "小明",
            "email": "xiaoming@test.com",
            "qq_number": "123456",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "小明"
        assert data["email"] == "xiaoming@test.com"
        assert data["qq_number"] == "123456"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_child_without_qq(self, client: AsyncClient, auth_headers: dict):
        """Creating a child without QQ number should succeed (optional field)."""
        response = await client.post("/api/children", json={
            "name": "无QQ孩子",
            "email": "noqq@test.com",
        }, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["qq_number"] == ""

    @pytest.mark.asyncio
    async def test_create_child_missing_name(self, client: AsyncClient, auth_headers: dict):
        """Creating a child without name should fail validation."""
        response = await client.post("/api/children", json={
            "email": "noname@test.com",
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_child_missing_email(self, client: AsyncClient, auth_headers: dict):
        """Creating a child without email should fail validation."""
        response = await client.post("/api/children", json={
            "name": "无邮箱孩子",
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_child_invalid_email(self, client: AsyncClient, auth_headers: dict):
        """Creating a child with invalid email format should fail."""
        response = await client.post("/api/children", json={
            "name": "坏邮箱",
            "email": "not-an-email",
        }, headers=auth_headers)
        assert response.status_code == 422


class TestUpdateChild:
    """Tests for PUT /api/children/{child_id}"""

    @pytest.mark.asyncio
    async def test_update_child_name(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Updating a child's name should succeed."""
        response = await client.put(f"/api/children/{child_id}", json={
            "name": "小明改名字了",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "小明改名字了"

    @pytest.mark.asyncio
    async def test_update_child_email(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Updating a child's email should succeed."""
        response = await client.put(f"/api/children/{child_id}", json={
            "email": "newemail@test.com",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "newemail@test.com"

    @pytest.mark.asyncio
    async def test_update_child_qq_number(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Updating a child's QQ number should succeed."""
        response = await client.put(f"/api/children/{child_id}", json={
            "qq_number": "999999",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["qq_number"] == "999999"

    @pytest.mark.asyncio
    async def test_update_nonexistent_child(self, client: AsyncClient, auth_headers: dict):
        """Updating a non-existent child should return 404."""
        response = await client.put("/api/children/9999", json={
            "name": "不存在",
        }, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteChild:
    """Tests for DELETE /api/children/{child_id}"""

    @pytest.mark.asyncio
    async def test_delete_child_success(self, client: AsyncClient, auth_headers: dict, child_id: int):
        """Deleting an existing child should succeed."""
        response = await client.delete(f"/api/children/{child_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify child is gone
        list_response = await client.get("/api/children", headers=auth_headers)
        assert len(list_response.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_child(self, client: AsyncClient, auth_headers: dict):
        """Deleting a non-existent child should return 404."""
        response = await client.delete("/api/children/9999", headers=auth_headers)
        assert response.status_code == 404
