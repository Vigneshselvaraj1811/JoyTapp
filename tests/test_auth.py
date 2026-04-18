import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.mark.asyncio
async def test_register_success():
    mock_auth_service = AsyncMock()
    mock_auth_service.register.return_value = {
        "user": {
            "id": "abc123",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
        "access_token": "mock_access",
        "refresh_token": "mock_refresh",
        "token_type": "bearer",
    }

    from app.core.dependencies import get_auth_service
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
            "full_name": "Test User",
        })

    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "tokens" in data["data"]


@pytest.mark.asyncio
async def test_login_success():
    mock_auth_service = AsyncMock()
    mock_auth_service.login.return_value = {
        "access_token": "mock_access",
        "refresh_token": "mock_refresh",
        "token_type": "bearer",
    }

    from app.core.dependencies import get_auth_service
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123",
        })

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["access_token"] == "mock_access"


@pytest.mark.asyncio
async def test_register_invalid_username():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "username": "u",   # too short
            "email": "test@example.com",
            "password": "SecurePass123",
            "full_name": "Test User",
        })
    assert response.status_code == 422
