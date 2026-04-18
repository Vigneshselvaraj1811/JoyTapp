from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.core.config import settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongodb.db = mongodb.client[settings.MONGO_DB_NAME]
    await _create_indexes()
    print(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("🔌 MongoDB connection closed")


async def _create_indexes():
    db = mongodb.db

    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)

    # Refresh tokens
    await db.refresh_tokens.create_index("token", unique=True)
    await db.refresh_tokens.create_index("user_id")
    await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)

    # Posts
    await db.posts.create_index("author_id")
    await db.posts.create_index("created_at")
    await db.posts.create_index("title")
    await db.posts.create_index([("title", "text")])
    await db.posts.create_index("is_deleted")

    # Likes
    await db.likes.create_index([("post_id", 1), ("user_id", 1)], unique=True)

    # Comments
    await db.comments.create_index("post_id")
    await db.comments.create_index("created_at")

    print("MongoDB indexes created")


def get_db() -> AsyncIOMotorDatabase:
    return mongodb.db
