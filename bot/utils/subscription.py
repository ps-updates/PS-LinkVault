# Cleaned & Refactored by @Mak0912 (TG)

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from info import Config


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
