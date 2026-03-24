from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle

from bot.database import is_verified, create_verification_token
from bot.utils import get_shortlink, get_readable_time
from info import Config


@Client.on_message(filters.command("token") & filters.private)
async def token_handler(client, message):
    user = message.from_user

    # If already verified
    if await is_verified(user.id):
        return await message.reply_text(
            "✅ <b>You are already verified!</b>\n\n"
            "No need to generate a new token."
        )

    # Generate token
    token = await create_verification_token(user.id)

    # Generate shortlink
    try:
        short_url = await get_shortlink(
            Config.SHORTLINK_API,
            Config.SHORTLINK_URL,
            f"https://t.me/{client.username}?start=verify-{user.id}-{token}"
        )
    except Exception:
        return await message.reply_text(
            "⚠️ <b>Shortlink generation failed!</b>\n"
            "Please try again later."
        )

    # 🔥 PREMIUM BUTTONS
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🚀 Get Token",
                url=short_url,
                style=ButtonStyle.SUCCESS
            )
        ],
        [
            InlineKeyboardButton(
                "🎥 How to Use",
                url=Config.TUTORIAL,
                style=ButtonStyle.PRIMARY
            )
        ]
    ])

    # 🔥 PREMIUM MESSAGE UI
    await message.reply_text(
        f"<b>🔐 Access Token System</b>\n\n"
        f"⚡ <b>Token Validity:</b> {get_readable_time(Config.TOKEN_EXPIRE)}\n\n"
        f"📌 Complete the process to unlock access.\n"
        f"After verification, you can use all shared links.\n\n"
        f"👇 <b>Click below to generate your token</b>",
        reply_markup=buttons
    )