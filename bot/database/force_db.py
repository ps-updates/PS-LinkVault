import datetime
from datetime import timezone
from .connection import db


class ForceChannelDB:
    """
    FSUB channel database.

    Stores:
        - channel_id
        - mode                  ("fsub" / "request")
        - invite_link_normal    (normal invite link)
        - invite_link_request   (join-request link)
        - created_at
        - updated_at
    """

    def __init__(self):
        self.col = db.force_channels

    async def initialize(self):
        """Ensure unique index for channel_id."""
        try:
            await self.col.create_index("channel_id", unique=True)
        except:
            pass



    # -------------------------------------------------------
    # NEW: ADD FULL CHANNEL WITH BOTH LINKS
    # -------------------------------------------------------
    async def add_channel_full(
        self,
        channel_id: int,
        mode: str,
        invite_link_normal: str,
        invite_link_request: str,
    ):
        """
        Insert a new channel entry with:
        - both invite links
        - explicit mode
        """

        now = datetime.datetime.now(timezone.utc)

        await self.col.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "mode": mode,
                    "invite_link_normal": invite_link_normal,
                    "invite_link_request": invite_link_request,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

    # -------------------------------------------------------
    # NEW: UPDATE MODE ONLY
    # -------------------------------------------------------
    async def update_channel_mode(self, channel_id: int, mode: str):
        await self.col.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "mode": mode,
                    "updated_at": datetime.datetime.now(timezone.utc),
                }
            }
        )

    # -------------------------------------------------------
    # NEW: UPDATE BOTH INVITE LINKS
    # -------------------------------------------------------
    async def update_links(self, channel_id: int, normal: str, request: str):
        await self.col.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "invite_link_normal": normal,
                    "invite_link_request": request,
                    "updated_at": datetime.datetime.now(timezone.utc),
                }
            }
        )

    # -------------------------------------------------------
    # GET SINGLE CHANNEL
    # -------------------------------------------------------
    async def get_channel(self, channel_id: int):
        return await self.col.find_one({"channel_id": channel_id})
        

    # -------------------------------------------------------
    # GET ALL CHANNELS
    # -------------------------------------------------------
    async def get_all_channels(self):
        return await self.col.find({}).sort("created_at", 1).to_list(None)

    
    async def get_all_ids(self):
        """
        Returns list of channel_id.
        """
        cursor = self.col.find({}, {"channel_id": 1})
        return [doc["channel_id"] for doc in await cursor.to_list(None)]
    

    # -------------------------------------------------------
    # EXISTS
    # -------------------------------------------------------
    async def exists(self, channel_id: int) -> bool:
        return await self.col.count_documents({"channel_id": channel_id}, limit=1) > 0

    # -------------------------------------------------------
    # DELETE
    # -------------------------------------------------------
    async def delete_channel(self, channel_id: int):
        await self.col.delete_one({"channel_id": channel_id})

    # -------------------------------------------------------
    # WIPE
    # -------------------------------------------------------
    async def wipe_channels(self):
        await self.col.delete_many({})


force_db = ForceChannelDB()
