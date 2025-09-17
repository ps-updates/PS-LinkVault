# Cleaned & Refactored by @Mak0912 (TG)

import asyncio, logging
from datetime import datetime, timedelta
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from info import Config
from bot.database import join_db



logger = logging.getLogger(__name__)


async def check_force_request(client, message, expire_seconds=600):
    user_id = message.from_user.id
    if user_id in Config.ADMINS or user_id == Config.OWNER_ID:
        return True

    async def process_channel(channel_id):
        if not channel_id:
            return None

        # ✅ Already cached in DB
        if await join_db.has_joined_channel(user_id, channel_id):
            return None

        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status != ChatMemberStatus.BANNED:
                # ✅ User is already in channel
                await join_db.add_join_req(user_id, channel_id)
                return None
        except UserNotParticipant:
            pass  # ❌ Not joined
        except Exception as e:
            logger.error(f"Error checking membership in {channel_id}: {e}")
            return None

        # ❌ Not joined → need to generate fresh invite link
        try:
            chat, invite = await asyncio.gather(
                client.get_chat(channel_id),
                client.create_chat_invite_link(
                    chat_id=channel_id,
                    creates_join_request=True,
                    expire_date=datetime.utcnow() + timedelta(seconds=expire_seconds)
                )
            )
            return InlineKeyboardButton(f"🎗 Request Join {chat.title}", url=invite.invite_link)

        except ChatAdminRequired:
            logger.warning(f"Bot is not admin in {channel_id}")
        except Exception as e:
            logger.warning(f"Invite link error for {channel_id}: {e}")

        return None

    # 🚀 Run all membership + invite link creation concurrently
    results = await asyncio.gather(*(process_channel(ch) for ch in Config.FORCE_SUB_CHANNEL))

    # Collect buttons
    buttons = [[btn] for btn in results if btn]

    if buttons:
        # Retry button
        try:
            payload = message.command[1]
            buttons.append([
                InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start={payload}")
            ])
        except Exception:
            pass

        await client.send_message(
            chat_id=user_id,
            text="**🚨 You must request to join the following channels before using this bot!**",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
        return False

    return True

    

async def handle_force_sub(client, message: Message):
    user = message.from_user
    not_joined = []
    joined = []
    buttons = []

    # Use preloaded channel info from client.channels_info
    for ch in Config.FORCE_SUB_CHANNEL:
        info = client.channel_info.get(ch)
        title = info.get("title", "Channel") if info else "Channel"

        try:
            member = await client.get_chat_member(ch, user.id)
            if member.status in (
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
            ):
                joined.append(ch)
            else:
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)

    # If user joined all channels, no need to prompt
    if not not_joined:
        return False

    # Create join buttons using preloaded invite links
    for ch in not_joined:
        info = client.channel_info.get(ch)
        if not info:
            continue
        url = info.get("invite_link")
        title = info.get("title", "Channel")
        if not url:
            continue
        buttons.append([InlineKeyboardButton(f"📢 {title}", url=url)])

    # Retry button if start payload present
    if len(message.command) > 1:
        payload = message.command[1]
        buttons.append([
            InlineKeyboardButton("🔁 Try Again", url=f"https://t.me/{client.username}?start={payload}")
        ])

    # Build channel join status text
    joined_txt = ""
    for ch in Config.FORCE_SUB_CHANNEL:
        info = client.channel_info.get(ch)
        title = info.get("title", "Channel") if info else "Channel"
        if ch in joined:
            joined_txt += f"✅ <b>{title}</b>\n"
        else:
            joined_txt += f"❌ <b>{title}</b>\n"

    # Format FSUB message
    fsub_msg = Config.FORCE_MSG.format(
        first=user.first_name,
        last=user.last_name,
        username=f"@{user.username}" if user.username else "N/A",
        mention=user.mention,
        id=user.id
    )

    # Send final FSUB reply
    await message.reply(
        f"{fsub_msg}\n\n<b>Channel Join Status:</b>\n{joined_txt}",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    return True
