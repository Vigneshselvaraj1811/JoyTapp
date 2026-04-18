from typing import Any, Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone


def to_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception:
        return None


def serialize_doc(doc: Dict) -> Dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc


class BaseRepository:
    collection_name: str = ""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.collection_name]

    async def find_by_id(self, id: str) -> Optional[Dict]:
        oid = to_object_id(id)
        if not oid:
            return None
        doc = await self.collection.find_one({"_id": oid})
        return serialize_doc(doc) if doc else None

    async def find_one(self, query: Dict) -> Optional[Dict]:
        doc = await self.collection.find_one(query)
        return serialize_doc(doc) if doc else None

    async def find_many(
        self,
        query: Dict,
        skip: int = 0,
        limit: int = 10,
        sort_field: str = "created_at",
        sort_order: int = -1,
    ) -> List[Dict]:
        cursor = self.collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [serialize_doc(doc) for doc in docs]

    async def count(self, query: Dict) -> int:
        return await self.collection.count_documents(query)

    async def insert_one(self, data: Dict) -> Dict:
        now = datetime.now(timezone.utc)
        data["created_at"] = now
        data["updated_at"] = now
        result = await self.collection.insert_one(data)
        data["id"] = str(result.inserted_id)
        data.pop("_id", None)
        return data

    async def update_one(self, id: str, update_data: Dict) -> Optional[Dict]:
        oid = to_object_id(id)
        if not oid:
            return None
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": oid}, {"$set": update_data})
        return await self.find_by_id(id)

    async def delete_one(self, id: str) -> bool:
        oid = to_object_id(id)
        if not oid:
            return False
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0

    async def soft_delete(self, id: str) -> Optional[Dict]:
        return await self.update_one(id, {"is_deleted": True, "deleted_at": datetime.now(timezone.utc)})
