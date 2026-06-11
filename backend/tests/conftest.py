import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app
from tests.test_db import test_engine, test_async_session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Override the dependency in the app
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_token(client: AsyncClient):
    """Register a test user and return the auth token."""
    response = await client.post("/api/auth/register", json={
        "username": "testparent",
        "password": "test123456",
        "email": "parent@test.com",
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str):
    """Return authorization headers with a valid token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def child_id(client: AsyncClient, auth_headers: dict):
    """Create a test child and return its ID."""
    response = await client.post("/api/children", json={
        "name": "小明",
        "email": "xiaoming@test.com",
        "qq_number": "123456",
    }, headers=auth_headers)
    return response.json()["id"]
