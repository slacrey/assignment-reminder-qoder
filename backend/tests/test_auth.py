"""Tests for authentication API endpoints."""
import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for POST /api/auth/register"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Successful registration should return a JWT token."""
        response = await client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "password123",
            "email": "newuser@test.com",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient):
        """Registering with an existing username should fail."""
        payload = {
            "username": "duplicate_user",
            "password": "password123",
            "email": "first@test.com",
        }
        await client.post("/api/auth/register", json=payload)
        # Second attempt with same username
        payload["email"] = "second@test.com"
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Registration with missing fields should return validation error."""
        response = await client.post("/api/auth/register", json={
            "username": "noemail",
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Registration with invalid email format should fail."""
        response = await client.post("/api/auth/register", json={
            "username": "bademail",
            "password": "password123",
            "email": "not-an-email",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Login with correct credentials should return a token."""
        # Register first
        await client.post("/api/auth/register", json={
            "username": "loginuser",
            "password": "password123",
            "email": "login@test.com",
        })
        # Then login
        response = await client.post("/api/auth/login", json={
            "username": "loginuser",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Login with wrong password should fail with 401."""
        await client.post("/api/auth/register", json={
            "username": "wrongpw_user",
            "password": "password123",
            "email": "wrongpw@test.com",
        })
        response = await client.post("/api/auth/login", json={
            "username": "wrongpw_user",
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with non-existent user should fail with 401."""
        response = await client.post("/api/auth/login", json={
            "username": "ghost_user",
            "password": "password123",
        })
        assert response.status_code == 401


class TestAuthProtection:
    """Tests for JWT authentication protection on protected endpoints."""

    @pytest.mark.asyncio
    async def test_access_without_token(self, client: AsyncClient):
        """Accessing protected endpoints without a token should fail."""
        response = await client.get("/api/children")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_with_invalid_token(self, client: AsyncClient):
        """Accessing protected endpoints with an invalid token should fail."""
        response = await client.get(
            "/api/children",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401
