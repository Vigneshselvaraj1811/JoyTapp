import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.main import app


MOCK_POST = {
    "id": "post123",
    "title": "Hello World",
    "content": "This is a test post",
    "author_id": "user123",
    "tags": ["test"],
    "image_url": None,
    "likes_count": 0,
    "comments_count": 0,
    "is_deleted": False,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


@pytest.mark.asyncio
async def test_list_posts_no_auth():
    mock_post_service = AsyncMock()
    mock_post_service.get_posts.return_value = {
        "items": [MOCK_POST],
        "total": 1,
        "page": 1,
        "page_size": 10,
        "total_pages": 1,
    }

    from app.core.dependencies import get_post_service
    app.dependency_overrides[get_post_service] = lambda: mock_post_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/posts")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_create_post_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/posts", json={
            "title": "New Post",
            "content": "Content here",
        })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_post_by_id():
    mock_post_service = AsyncMock()
    mock_post_service.get_post.return_value = MOCK_POST

    from app.core.dependencies import get_post_service
    app.dependency_overrides[get_post_service] = lambda: mock_post_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/posts/post123")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "post123"
