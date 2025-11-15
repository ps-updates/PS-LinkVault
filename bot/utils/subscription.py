
import asyncio
import logging
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import Config
from bot.database import join_db, force_db

logger = logging.getLogger(__name__)


async def force_sub_required(client, message):
    user = message.from_user
    user_id = user.id

    # 🛡 Admin bypass
    if user_id in Config.ADMINS or user_id == Config.OWNER_ID:
        return True

    channels = await force_db.get_all_channels()
    must_block = False
    keyboard_rows = []     # final reply keyboard

    valid_status = {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    }

    async def check(ch):
        nonlocal must_block, keyboard_rows

        ch_id = ch["channel_id"]
        mode = ch["mode"] 
        normal = ch.get("invite_link_normal")
        req = ch.get("invite_link_request")

        # active link based on mode
        link = normal if mode == "fsub" else req
        label = "🔒 Must Join" if mode == "fsub" else "📢 Must Join"

        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status in valid_status:
                await join_db.add_join_req(user_id, ch_id)
                return
        except Exception as e:
            logger.debug(f"User {user_id} not in channel {ch_id}: {e}")

        # ❌ User NOT joined
        must_block = True
        link = link or "https://t.me"     # fallback

        # add URL button manually
        keyboard_rows.append([
            InlineKeyboardButton(label, url=link)
        ])

    # run all checks concurrently
    await asyncio.gather(*(check(ch) for ch in channels))

    # ✅ all channels joined
    if not must_block:
        return True

    # 🔄 Add "I Joined" retry button
    try:
        payload = message.command[1]
        retry_url = f"https://t.me/{client.username}?start={payload}"

        keyboard_rows.append([
            InlineKeyboardButton("🔄 I Joined, Check Again", url=retry_url)
        ])
    except:
        pass

    # final manual keyboard
    keyboard = InlineKeyboardMarkup(keyboard_rows)

    await message.reply(
        "**🚨 You must join all required channels to use this bot.**",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    return False
