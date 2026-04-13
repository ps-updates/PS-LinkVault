import asyncio
import sys
from pyrogram import idle
from bot import Bot

if sys.platform != "win32":
    import uvloop

    uvloop.install()

async def main():
    app = Bot()
    await app.start()
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
