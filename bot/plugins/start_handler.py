# Cleaned & Refactored by @Mak0912 (TG)

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from info import Config
from bot.utils import is_subscribed, handle_force_sub, decode, get_messages, schedule_auto_delete
from bot.database import add_user, present_user

# ──────────────────────────────────────────────────────────────

@Client.on_message(filters.command('start') & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if not await present_user(user_id):
        await add_user(user_id)

    if not await is_subscribed(client, user_id):
        return await handle_force_sub(client, message)

    if len(message.command) > 1:
        try:
            encoded = message.command[1]
            decoded = decode(encoded)
            parts = decoded.split("-")
        except Exception:
            return

        try:
            if len(parts) == 3:
                start_id = int(int(parts[1]) / abs(client.db_channel.id))
                end_id = int(int(parts[2]) / abs(client.db_channel.id))
                ids = range(start_id, end_id + 1) if start_id <= end_id else list(range(start_id, end_id - 1, -1))
            elif len(parts) == 2:
                ids = [int(int(parts[1]) / abs(client.db_channel.id))]
            else:
                return
        except Exception:
            return

        wait_msg = await message.reply("Processing Please wait...")

        try:
            messages = await get_messages(client, ids)
        except Exception:
            return await wait_msg.edit("❌ Something went wrong while fetching messages!")

        await wait_msg.delete()

        to_delete = []

        for msg in messages:
            caption = ""
            if Config.CUSTOM_CAPTION and msg.document:
                caption = Config.CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name
                )
            else:
                caption = msg.caption.html if msg.caption else ""

            markup = msg.reply_markup if Config.DISABLE_CHANNEL_BUTTON else None

            try:
                sent = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup,
                    protect_content=Config.PROTECT_CONTENT
                )
                if Config.AUTO_DELETE_TIME:
                    to_delete.append(sent)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                client.log(__name__).info(f"Copy error: {e}")

        if to_delete:
            note = await client.send_message(user_id, Config.AUTO_DELETE_MSG.format(time=Config.AUTO_DELETE_TIME))
            asyncio.create_task(schedule_auto_delete(to_delete, client, note))

    else:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😊 About Me", callback_data="about"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
        caption = Config.START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username="@" + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=user_id
        )

        if Config.START_PIC:
            await message.reply_photo(photo=Config.START_PIC, caption=caption, reply_markup=buttons, quote=True)
        else:
            await message.reply_text(text=caption, reply_markup=buttons, disable_web_page_preview=True, quote=True)

# ──────────────────────────────────────────────────────────────
