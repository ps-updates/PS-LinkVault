import secrets
from datetime import datetime, timedelta

from .connection import db

users_col = db["verified_users"]
tokens_col = db["verified_tokens"]

async def create_verification_token(user_id: int) -> str:
    token = secrets.token_urlsafe(16)
    await tokens_col.delete_many({"user_id": user_id})  # Remove old tokens
    await tokens_col.insert_one({
        "user_id": user_id,
        "token": token,
        "used": False,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=30)
    })
    return token

async def set_verified(user_id: int, expire_seconds: int):
    expires_at = datetime.utcnow() + timedelta(seconds=expire_seconds)
    await users_col.update_one(
        {"_id": user_id},
        {"$set": {"is_verified": True, "expires_at": expires_at}},
        upsert=True
    )

async def is_verified(user_id: int) -> bool:
    user = await users_col.find_one({"_id": user_id})
    if not user or not user.get("is_verified"):
        return False
    if datetime.utcnow() > user.get("expires_at", datetime.utcnow()):
        await users_col.update_one(
            {"_id": user_id},
            {"$set": {"is_verified": False}, "$unset": {"expires_at": ""}}
        )
        return False
    return True

async def validate_token_and_verify(user_id: int, token: str, expire_seconds: int) -> bool:
    record = await tokens_col.find_one({"token": token})
    if not record or record["used"] or record["user_id"] != user_id:
        return False
    if datetime.utcnow() > record["expires_at"]:
        return False
    await tokens_col.update_one({"_id": record["_id"]}, {"$set": {"used": True}})
    await set_verified(user_id, expire_seconds)
    return True
