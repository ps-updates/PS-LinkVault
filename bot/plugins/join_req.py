from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from bot.database import join_db
from info import Config

def is_auth_req_channel(_, __, update):
    return update.chat.id in Config.FORCE_SUB_CHANNEL

@Client.on_chat_join_request(filters.create(is_auth_req_channel))
async def join_reqs(client, message: ChatJoinRequest):
    await join_db.add_join_req(message.from_user.id, message.chat.id)


@Client.on_message(filters.command("delreq") & filters.private & filters.user(Config.ADMINS))
async def del_requests(client, message):
    await join_db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
