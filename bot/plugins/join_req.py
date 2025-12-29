# Cleaned & Refactored by @Mak0912 (TG)

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from bot.database.force_db import force_db
from bot.database.join_request_db import join_db
from info import Config


def is_request_mode_channel(_, __, update: ChatJoinRequest):
    """
    ✅ DYNAMIC filter Now 
    """
    return force_db.is_request_mode_channel(update.chat.id)


@Client.on_chat_join_request(filters.create(is_request_mode_channel))
async def handle_join_requests(client, message: ChatJoinRequest):
    """
    Handle join requests for channels in "request" mode.
    """
    await join_db.add_join_req(message.from_user.id, message.chat.id)


@Client.on_message(filters.command("delreq") & filters.private & filters.user(Config.ADMINS))
async def delete_all_requests(client, message):
    """
    Admin command to wipe all stored join request records.
    """
    await join_db.del_join_req()    
    await message.reply("<b>⚙ Successfully deleted all channel join request records</b>")
