import asyncio
import logging
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
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
                return  # ✅ already joined
        except:
            pass

        # 🔹 REQUEST MODE
        if mode == "request":
            requested = await join_db.has_joined_channel(user_id, ch_id)
            if requested:
                return  # ✅ already requested

        # ❌ BLOCK USER
        must_block = True
        link = normal if mode == "fsub" else request

        if mode == "fsub":
            label = "🔒 Join Channel"
            style = ButtonStyle.PRIMARY
        else:
            label = "📢 Request Access"
            style = ButtonStyle.SUCCESS

        keyboard_rows.append([
            InlineKeyboardButton(label, url=link or "https://t.me", style=style)
        ])

    await asyncio.gather(*(check_channel(ch) for ch in channels))

    if not must_block:
        return True

    # 🔄 Retry Button
    try:
        payload = message.command[1]
        retry_url = f"https://t.me/{client.username}?start={payload}"

        keyboard_rows.append([
            InlineKeyboardButton(
                "🔄 I Joined / Continue",
                url=retry_url,
                style=ButtonStyle.SUCCESS
            )
        ])
    except:
        pass

    # 💬 PREMIUM MESSAGE UI
    await message.reply(
        "<b>🚨 Access Restricted</b>\n\n"
        "🔐 To use this bot, you must complete the required steps below.\n\n"
        "📌 Join or request access to all channels,\n"
        "then click <b>Continue</b>.\n\n"
        "👇 Follow the buttons below:",
        reply_markup=InlineKeyboardMarkup(keyboard_rows),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

    return False