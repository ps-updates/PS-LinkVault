# Cleaned & Refactored by @Mak0912 (TG)

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from info import Config
from bot.database import full_userbase, del_user

REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without any spaces.</code>"

@Client.on_message(filters.command("users") & filters.private & filters.user(Config.ADMINS))
async def show_user_count(client: Client, message: Message):
    msg = await message.reply("Processing Please wait....")
    users = await full_userbase()
    await msg.edit(f"<b>{len(users)} users are using this bot.</b>")

# ──────────────────────────────────────────────────────────────

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(Config.ADMINS))
async def broadcast_message(client: Client, message: Message):
    if not message.reply_to_message:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(5)
        return await msg.delete()

    users = await full_userbase()
    original = message.reply_to_message
    status = {
        "total": 0, 
        "sent": 0, 
        "blocked": 0, 
        "deleted": 0, 
        "failed": 0
    }

    wait = await message.reply("<i>Broadcasting message. Please wait...</i>")

    for user_id in users:
        try:
            await original.copy(user_id)
            status["sent"] += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await original.copy(user_id)
            status["sent"] += 1
        except UserIsBlocked:
            await del_user(user_id)
            status["blocked"] += 1
        except InputUserDeactivated:
            await del_user(user_id)
            status["deleted"] += 1
        except Exception:
            status["failed"] += 1
        status["total"] += 1

    summary = f"""<b><u>📢 Broadcast Summary</u></b>

👥 Total Users: <code>{status['total']}</code>
✅ Sent: <code>{status['sent']}</code>
⛔ Blocked: <code>{status['blocked']}</code>
❌ Deleted: <code>{status['deleted']}</code>
⚠️ Failed: <code>{status['failed']}</code>"""

    await wait.edit(summary)
