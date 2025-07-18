# Cleaned & Refactored by @Mak0912 (TG)

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import Config
from bot.utils import encode, get_message_id

MAX_ATTEMPTS = 3 

async def get_valid_post(client: Client, user_id: int, prompt_text: str) -> int:
    """
    Prompts user to forward a message or provide a link from the DB Channel,
    and retries until MAX_ATTEMPTS is reached.
    """
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        try:
            response = await client.ask(
                chat_id=user_id,
                text=prompt_text,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except Exception:
            return 0

        msg_id = await get_message_id(client, response)
        if msg_id:
            return msg_id

        await response.reply(
            "❌ This message is not from the DB Channel or the link is invalid.",
            quote=True
        )
        attempts += 1

    await client.send_message(
        chat_id=user_id,
        text="⛔️ You've reached the maximum number of attempts. Please try again later.",
        quote=True
    )
    return 0

@Client.on_message(filters.private & filters.user(Config.ADMINS) & filters.command("batch"))
async def batch_link_generator(client: Client, message: Message):
    user_id = message.from_user.id

    start_prompt = "📥 Forward the *first* message from the DB Channel (or send the link):"
    end_prompt = "📤 Forward the *last* message from the DB Channel (or send the link):"

    first_id = await get_valid_post(client, user_id, start_prompt)
    if not first_id:
        return

    last_id = await get_valid_post(client, user_id, end_prompt)
    if not last_id:
        return

    encoded = encode(f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}")
    full_link = f"https://t.me/{client.username}?start={encoded}"

    button = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={full_link}')]])
    await message.reply_text(
        f"<b>✅ Batch Link Generated</b>\n\n{full_link}",
        quote=True,
        reply_markup=button 
    )

@Client.on_message(filters.private & filters.user(Config.ADMINS) & filters.command("genlink"))
async def single_link_generator(client: Client, message: Message):
    user_id = message.from_user.id

    prompt = "📩 Forward the message from the DB Channel (or send the link):"
    msg_id = await get_valid_post(client, user_id, prompt)
    if not msg_id:
        return

    encoded = encode(f"get-{msg_id * abs(client.db_channel.id)}")
    full_link = f"https://t.me/{client.username}?start={encoded}"

    button = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={full_link}')]])

    await message.reply_text(
        f"<b>✅ Direct Link Generated</b>\n\n{full_link}",
        quote=True,
        reply_markup=button
    )
