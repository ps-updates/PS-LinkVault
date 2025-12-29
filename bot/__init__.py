import sys
import asyncio
from datetime import datetime
from pyrogram import Client
from logger import LOGGER
from info import Config
from bot.utils import schedule_manager
from bot.database import force_db, join_db

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
        
        # 🔐 Initialize DB + request-mode cache
        await force_db.initialize()
        await join_db.initialize()
        
        me = await self.get_me()
        self.username = me.username
        self.mention = me.mention
        self.first_name = me.first_name
        self.uptime = datetime.now()
         
        channels = await force_db.get_all_channels()
        if not channels:
            self.log(__name__).info("FSUB is currently disabled (no channels configured)")
            
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
