from pyrogram import Client, filters
from pyrogram.types import Message
from info import Config
from datetime import datetime
from bot.utils import get_readable_time

@Client.on_message(filters.command('stats') & filters.user(Config.ADMINS))
async def stats(bot: Client, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds, long=True)
    await message.reply(Config.BOT_STATS_TEXT.format(uptime=time))

'''
#Not need If You comment out this one 
#then you will face issues on token verification
@Client.on_message(filters.private & filters.incoming)
async def useless(_,message: Message):
    if Config.USER_REPLY_TEXT:
        await message.reply(Config.USER_REPLY_TEXT)'''
