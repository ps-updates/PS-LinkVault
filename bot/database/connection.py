from pymongo import AsyncMongoClient
from info import Config

client = AsyncMongoClient(Config.DATABASE_URL)
db = client[Config.DATABASE_NAME]
