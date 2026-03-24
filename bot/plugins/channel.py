# Cleaned & Premium UI Version

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from pyrogram.enums import ButtonStyle
from pyrogram.errors import FloodWait

from info import Config
from bot.utils import encode


@Client.on_message(filters.private & filters.user(Config.ADMINS) & filters.media)
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("⏳ <b>Please wait...</b>")

    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except Exception as e:
        print(e)
        await reply_text.edit_text("❌ <b>Something went wrong!</b>")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    # 🔥 PREMIUM BUTTONS
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Open Link", url=link, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton(
                "🔁 Share",
                url=f'https://telegram.me/share/url?url={link}',
                style=ButtonStyle.SUCCESS
            )
        ]
    ])

    await reply_text.edit(
        f"<b>✅ Your Link is Ready</b>\n\n"
        f"🔗 <code>{link}</code>\n\n"
        f"📌 Use the buttons below to open or share.",
        reply_markup=reply_markup,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

    if not Config.DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await post_message.edit_reply_markup(reply_markup)
        except Exception:
            pass


@Client.on_message(filters.channel & filters.incoming & filters.chat(Config.CHANNEL_ID))
async def new_post(client: Client, message: Message):

    if Config.DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    # 🔥 SAME PREMIUM BUTTONS
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Open Link", url=link, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton(
                "🔁 Share",
                url=f'https://telegram.me/share/url?url={link}',
                style=ButtonStyle.SUCCESS
            )
        ]
    ])

    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass
