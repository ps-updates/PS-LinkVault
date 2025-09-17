import datetime
from .connection import db

class JoinRequestDB:
    def __init__(self):
        self.req = db.join_requests
        self._initialized = False

    async def initialize(self):
        """
        Initialize the database collection with indexes
        """
        if not self._initialized:
            try:
                # Create index asynchronously
                await self.req.create_index("user_id", unique=True)
                self._initialized = True
            except Exception as e:
                # Handle duplicate key error (index already exists)
                if "already exists" in str(e).lower() or "duplicate key" in str(e).lower():
                    self._initialized = True
                    print("JoinRequestDB index already exists")
                else:
                    print(f"Warning: Failed to create index: {e}")
                    # Continue without failing
                    self._initialized = True

    async def add_join_req(self, user_id: int, channel_id: int):
        """
        Store that a user requested to join a specific channel.
        """
        if not self._initialized:
            await self.initialize()
            
        await self.req.update_one(
            {'user_id': user_id},
            {
                '$addToSet': {'channels': channel_id},
                '$setOnInsert': {'created_at': datetime.datetime.utcnow()}
            },
            upsert=True
        )

    async def has_joined_channel(self, user_id: int, channel_id: int) -> bool:
        """
        Check if the user already has a pending/join request stored.
        """
        if not self._initialized:
            await self.initialize()
            
        doc = await self.req.find_one({'user_id': user_id})
        return doc and 'channels' in doc and channel_id in doc['channels']

    async def find_join_req(self, user_id: int) -> bool:
        """
        Returns True if any join request exists for this user.
        """
        if not self._initialized:
            await self.initialize()
            
        return bool(await self.req.find_one({'user_id': user_id}))

    async def del_join_req(self, user_id: int = None):
        """
        Delete join requests. If user_id is given, delete only for that user.
        Otherwise drop all.
        """
        if not self._initialized:
            await self.initialize()
            
        if user_id:
            await self.req.delete_one({'user_id': user_id})
        else:
            await self.req.drop()

join_db = JoinRequestDB()
