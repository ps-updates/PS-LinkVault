# Cleaned & Refactored by @Mak0912 (TG)

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from info import Config
from bot.utils import handle_force_sub, check_force_request, decode, get_messages, get_readable_time, schedule_manager
from bot.database import add_user, present_user, is_verified, validate_token_and_verify

# ──────────────────────────────────────────────────────────────

@Client.on_message(filters.command('start') & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if not await present_user(user_id):
        await add_user(user_id)

    if Config.JOIN_REQUEST_ENABLE:
        if not await check_force_request(client, message, expire_seconds=600):
            return
    else:
        if not await handle_force_sub(client, message):
            return

    if len(message.command) > 1:
        param = message.command[1]

        # ✅ New style verification: /start verify-USERID-TOKEN
        if param.startswith("verify-"):
            parts = param.split("-", 2)
            if len(parts) == 3:
                _, uid, token = parts
                if str(uid) != str(user_id):
                    return await message.reply("❌ Invalid or expired link!")
                verified = await validate_token_and_verify(user_id, token, Config.TOKEN_EXPIRE)
                if verified:
                    return await message.reply("✅ You’ve been verified successfully!")
                else:
                    return await message.reply("❌ Invalid or expired token. Please use /token to generate a new one.")
            else:
                return await message.reply("❌ Malformed verification link.")

        # 🔐 Existing deep link decoder
        try:
            decoded = decode(param)
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

        # ✅ Check verification only if required
        if Config.VERIFY_MODE and (user_id not in Config.ADMINS or user_id != Config.OWNER_ID):
            if not await is_verified(user_id):
                return await message.reply_text(
                    f"🔐 You're not verified!\nPlease verify yourself first using /token.",
                    disable_web_page_preview=True
                )

        wait_msg = await message.reply("Processing... Please wait.")

        try:
            messages = await get_messages(client, ids)
        except Exception:
            return await wait_msg.edit("❌ Error while fetching messages!")

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
            files_to_delete = [msg.id for msg in to_delete]
            delete_at = Config.AUTO_DELETE_TIME
            
            warning = await client.send_message(user_id, Config.AUTO_DELETE_MSG.format(time=get_readable_time(Config.AUTO_DELETE_TIME)))
            if warning:
                files_to_delete.append(warning.id)
                
            await schedule_manager.schedule_delete(
                client=client,
                chat_id=message.chat.id,
                message_ids=files_to_delete,
                delete_n_seconds=delete_at,
                base64_file_link=param,        
            )
    else:
        # Start Message / No Params
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
