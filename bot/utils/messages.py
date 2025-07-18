# Cleaned & Refactored by @Mak0912 (TG)

import re, asyncio
from pyrogram.errors import FloodWait

async def get_messages(client, message_ids):
    messages, total = [], 0
    while total != len(message_ids):
        batch = message_ids[total:total+200]
        try:
            msgs = await client.get_messages(client.db_channel.id, batch)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(client.db_channel.id, batch)
        except Exception:
            msgs = []
        total += len(batch)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat and message.forward_from_chat.id == client.db_channel.id:
        return message.forward_from_message_id

    if message.text:
        match = re.match(r"https://t.me/(?:c/)?(.*)/(\d+)", message.text)
        if match:
            chan_id, msg_id = match.groups()
            msg_id = int(msg_id)
            if chan_id.isdigit():
                return msg_id if f"-100{chan_id}" == str(client.db_channel.id) else 0
            else:
                return msg_id if chan_id == client.db_channel.username else 0
    return 0
