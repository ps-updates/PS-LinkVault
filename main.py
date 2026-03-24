import uvloop
import asyncio
from pyrogram import idle
from bot import Bot

uvloop.install()

async def main():
    app = Bot()
    await app.start()
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
