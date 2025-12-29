import asyncio
import logging
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import Config
from bot.database import force_db, join_db

logger = logging.getLogger(__name__)


async def force_sub_required(client, message):
    user = message.from_user
    user_id = user.id

    # 🛡 Admin / Owner bypass
    if user_id in Config.ADMINS or user_id == Config.OWNER_ID:
        return True

    channels = await force_db.get_all_channels()

    # 📴 FSUB OFF
    if not channels:
        return True

    must_block = False
    keyboard_rows = []

    valid_status = {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    }

    async def check_channel(ch):
        nonlocal must_block, keyboard_rows

        ch_id = ch["channel_id"]
        mode = ch["mode"]
        normal = ch.get("invite_link_normal")
        request = ch.get("invite_link_request")

        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status in valid_status:
                return  # ✅ joined
        except:
            pass

        # 🔹 REQUEST MODE CASE
        if mode == "request":
            requested = await join_db.has_joined_channel(user_id, ch_id)
            if requested:
                return  # ✅ requested → allow

        # ❌ BLOCK
        must_block = True
        link = normal if mode == "fsub" else request
        label = "🔒 Join Channel" if mode == "fsub" else "📢 Request to Join"

        keyboard_rows.append([
            InlineKeyboardButton(label, url=link or "https://t.me")
        ])

    await asyncio.gather(*(check_channel(ch) for ch in channels))

    if not must_block:
        return True

    # 🔄 Retry button
    try:
        payload = message.command[1]
        retry_url = f"https://t.me/{client.username}?start={payload}"

        keyboard_rows.append([
            InlineKeyboardButton("🔄 I Joined / Requested", url=retry_url)
        ])
    except:
        pass

    await message.reply(
        "**🚨 You must join/request all required channels to use this bot.**",
        reply_markup=InlineKeyboardMarkup(keyboard_rows),
        disable_web_page_preview=True
    )

    return False
