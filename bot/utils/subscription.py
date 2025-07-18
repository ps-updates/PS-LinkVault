# Cleaned & Refactored by @Mak0912 (TG)

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from info import Config

async def is_subscribed(client: Client, user_id: int) -> bool:
    if not Config.FORCE_SUB_CHANNEL:
        return True
    if user_id in Config.ADMINS:
        return True

    try:
        member = await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
    except Exception:
        return False

    return member.status in (
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.MEMBER,
    )

async def handle_force_sub(client: Client, message: Message):
    try:
        if Config.JOIN_REQUEST_ENABLE:
            invite = await client.create_chat_invite_link(Config.FORCE_SUB_CHANNEL, creates_join_request=True)
        else:
            invite = await client.get_chat(Config.FORCE_SUB_CHANNEL)
        invite_link = invite.invite_link
    except Exception:
        invite_link = client.invitelink

    buttons = [[InlineKeyboardButton("📢 Join Channel", url=invite_link)]]

    if len(message.command) > 1:
        buttons.append([
            InlineKeyboardButton("🔁 Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")
        ])

    user = message.from_user
    caption = Config.FORCE_MSG.format(
        first=user.first_name,
        last=user.last_name,
        username=f"@{user.username}" if user.username else None,
        mention=user.mention,
        id=user.id
    )

    await message.reply(
        text=caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
