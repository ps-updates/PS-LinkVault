import sys
import asyncio
from datetime import datetime
from pyrogram import Client
from logger import LOGGER
from info import Config
from bot.utils import schedule_manager
from bot.database import force_db

ascii_art = """
████████╗██╗░░██╗███████╗  ██████╗░░██████╗  ██████╗░░█████╗░████████╗░██████╗
╚══██╔══╝██║░░██║██╔════╝  ██╔══██╗██╔════╝  ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
░░░██║░░░███████║█████╗░░  ██████╔╝╚█████╗░  ██████╦╝██║░░██║░░░██║░░░╚█████╗░
░░░██║░░░██╔══██║██╔══╝░░  ██╔═══╝░░╚═══██╗  ██╔══██╗██║░░██║░░░██║░░░░╚═══██╗
░░░██║░░░██║░░██║███████╗  ██║░░░░░██████╔╝  ██████╦╝╚█████╔╝░░░██║░░░██████╔╝
░░░╚═╝░░░╚═╝░░╚═╝╚══════╝  ╚═╝░░░░░╚═════╝░  ╚═════╝░░╚════╝░░░░╚═╝░░░╚═════╝░
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="PS-LinkVault",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="bot/plugins"),
            workers=Config.BOT_WORKERS,
            bot_token=Config.BOT_TOKEN
        )

        self.log = LOGGER
        
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.mention = me.mention
        self.uptime = datetime.now()
        await force_db.initialize()
        
        self.log(__name__).info("Starting FSUB sync...")
            
        # ------------------------------------------------------------
        # FSUB SYNC: Only add NEW channels, update links for all
        # ------------------------------------------------------------
        db_ids = await force_db.get_all_ids()

        # Convert config IDs to integers safely
        config_ids = []
        for raw in Config.FORCE_SUB_CHANNEL:
            try:
                config_ids.append(int(raw))
            except:
                self.log(__name__).warning(f"[FSUB] Invalid channel ID: {raw}")

        # NEW channels = in config but not in DB
        new_channels = [cid for cid in config_ids if cid not in db_ids]

        # ------------------------------------------------------------
        # 1) Handle NEW CHANNELS → Insert with mode = "fsub"
        # ------------------------------------------------------------
        for cid in new_channels:
            try:
                await self.get_chat_member(cid, "me")
            except Exception as e:
                self.log(__name__).warning(f"[FSUB] Bot is not in {cid}: {e}")
                continue

            try:
                normal_link = await self.export_chat_invite_link(cid)
                req = await self.create_chat_invite_link(cid, creates_join_request=True)
                request_link = req.invite_link

                await force_db.add_channel_full(
                    channel_id=cid,
                    mode="fsub",   # NEW CHANNEL → fsub only
                    invite_link_normal=normal_link,
                    invite_link_request=request_link
                )

                self.log(__name__).info(f"[FSUB] Added NEW channel {cid}")

            except Exception as e:
                self.log(__name__).warning(f"[FSUB] Failed to sync new channel {cid}: {e}")

        # ------------------------------------------------------------
        # 2) Handle EXISTING CHANNELS → Refresh links only
        # ------------------------------------------------------------
        for cid in db_ids:
            try:
                await self.get_chat_member(cid, "me")
            except:
                continue  # skip, bot not in channel

            # Get existing DB entry (preserve mode)
            entry = await force_db.get_channel(cid)
            mode = entry.get("mode", "fsub")

            try:
                normal_link = await self.export_chat_invite_link(cid)
                req = await self.create_chat_invite_link(cid, creates_join_request=True)
                request_link = req.invite_link

                # Update links only, DO NOT TOUCH MODE
                await force_db.update_links(cid, normal_link, request_link)

                self.log(__name__).info(
                    f"[FSUB] Updated links for {cid} (mode preserved: {mode})"
                )

            except Exception as e:
                self.log(__name__).warning(f"[FSUB] Failed updating links for {cid}: {e}")


        # ------------------------------------------------------------
        # Verify DB logging channel
        # ------------------------------------------------------------
        try:
            db_channel = await self.get_chat(Config.CHANNEL_ID)
            self.db_channel = db_channel

            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()

        except Exception as e:
            self.log(__name__).warning(e)
            self.log(__name__).warning(
                f"Make sure bot is admin in DB Channel (CHANNEL_ID={Config.CHANNEL_ID})"
            )
            self.log(__name__).info("Bot Stopped. Support: https://t.me/ps_discuss")
            sys.exit()

        
        print(ascii_art)
        await asyncio.sleep(1.5)
        self.log(__name__).info(f"Bot Running..!\nCreated by https://t.me/ps_updates")
        print("Welcome to File Sharing Bot")

        # schedule manager
        await schedule_manager.start()
        asyncio.create_task(schedule_manager.restore_pending_deletes(self))

        if Config.WEB_MODE:
            from web import start_webserver
            asyncio.create_task(start_webserver(self, Config.PORT))
        
    async def stop(self, *args):
        await super().stop()
        self.log(__name__).info("Bot stopped.")
