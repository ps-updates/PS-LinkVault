from motor.motor_asyncio import AsyncIOMotorClient
from info import Config

client = AsyncIOMotorClient(Config.DATABASE_URL)
db = client[Config.DATABASE_NAME]
