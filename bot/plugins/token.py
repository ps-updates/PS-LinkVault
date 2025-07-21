from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database import is_verified, create_verification_token
from bot.utils import get_shortlink, get_readable_time
from info import Config

@Client.on_message(filters.command("token") & filters.private)
async def token_handler(client, message):
    user = message.from_user

    # If already verified
    if await is_verified(user.id):
        return await message.reply_text(
            "✅ You are already verified! No need to generate a new token."
        )

    # Generate and store token
    token = await create_verification_token(user.id)

    # Create short link for /start=verify-<userid>-<token>
    try:
        short_url = await get_shortlink(
            Config.SHORTLINK_API,
            Config.SHORTLINK_URL,
            f"https://t.me/{client.username}?start=verify-{user.id}-{token}"
        )
    except Exception:
        return await message.reply_text("⚠️ Failed to generate shortlink. Please try again later.")

    # Prepare buttons
    buttons = [
        [InlineKeyboardButton("💫 Refresh Access Token", url=short_url)],
        [InlineKeyboardButton("🎥 Tutorial Video", url=Config.TUTORIAL)]
    ]

    # Send token message with buttons
    await message.reply_text(
        f"<i><b>🔐 Your New Access Token Generated:</b>\n\n⚠️ <b>Token Validity:</b> {get_readable_time(Config.TOKEN_EXPIRE)}.\n\nThis is an ads-based access token. If you pass 1 access token, you can access messages from sharable links for the next {get_readable_time(Config.TOKEN_EXPIRE)}.</i>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
