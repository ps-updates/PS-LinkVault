# Cleaned & Premium UI Version

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from info import Config
from bot.utils import encode, get_message_id

MAX_ATTEMPTS = 3 


# -----------------------------------------------------------
# 🔁 INPUT HANDLER
# -----------------------------------------------------------

async def get_valid_post(client: Client, user_id: int, prompt_text: str) -> int:
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
            "❌ <b>Invalid message!</b>\n"
            "Make sure it's from DB Channel or valid link."
        )
        attempts += 1

    await client.send_message(
        chat_id=user_id,
        text="⛔️ <b>Maximum attempts reached!</b>\nTry again later."
    )
    return 0


# -----------------------------------------------------------
# 🔗 BATCH LINK GENERATOR
# -----------------------------------------------------------

@Client.on_message(filters.private & filters.user(Config.ADMINS) & filters.command("batch"))
async def batch_link_generator(client: Client, message: Message):
    user_id = message.from_user.id

    start_prompt = (
        "📥 <b>Step 1:</b>\n"
        "Send the <b>FIRST</b> message or link"
    )

    end_prompt = (
        "📤 <b>Step 2:</b>\n"
        "Send the <b>LAST</b> message or link"
    )

    first_id = await get_valid_post(client, user_id, start_prompt)
    if not first_id:
        return

    last_id = await get_valid_post(client, user_id, end_prompt)
    if not last_id:
        return

    encoded = encode(f"get-{first_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}")
    full_link = f"https://t.me/{client.username}?start={encoded}"

    button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Open Link", url=full_link, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🔁 Share", url=f'https://telegram.me/share/url?url={full_link}', style=ButtonStyle.SUCCESS)
        ]
    ])

    await message.reply_text(
        f"<b>✅ Batch Link Generated</b>\n\n"
        f"🔗 <code>{full_link}</code>\n\n"
        f"📌 Use buttons below to open or share.",
        reply_markup=button
    )


# -----------------------------------------------------------
# 🔗 SINGLE LINK GENERATOR
# -----------------------------------------------------------

@Client.on_message(filters.private & filters.user(Config.ADMINS) & filters.command("genlink"))
async def single_link_generator(client: Client, message: Message):
    user_id = message.from_user.id

    prompt = (
        "📩 <b>Send Message</b>\n"
        "Forward from DB Channel or send link"
    )

    msg_id = await get_valid_post(client, user_id, prompt)
    if not msg_id:
        return

    encoded = encode(f"get-{msg_id * abs(client.db_channel.id)}")
    full_link = f"https://t.me/{client.username}?start={encoded}"

    button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Open Link", url=full_link, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🔁 Share", url=f'https://telegram.me/share/url?url={full_link}', style=ButtonStyle.SUCCESS)
        ]
    ])

    await message.reply_text(
        f"<b>✅ Direct Link Generated</b>\n\n"
        f"🔗 <code>{full_link}</code>\n\n"
        f"📌 Use buttons below to open or share.",
        reply_markup=button
    )