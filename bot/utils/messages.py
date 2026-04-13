# Cleaned & Refactored by @Mak0912 (TG)

import re
import asyncio
from pyrogram.errors import FloodWait


async def get_messages(client, message_ids):
    messages = []
    total = 0

    while total != len(message_ids):
        batch = message_ids[total: total + 200]

        try:
            msgs = await client.get_messages(client.db_channel.id, batch)

        except FloodWait as e:
            await asyncio.sleep(e.value or e.x)
            msgs = await client.get_messages(client.db_channel.id, batch)

        except Exception:
            msgs = []

        total += len(batch)
        messages.extend(msgs)

    return messages


async def get_message_id(client, message):
    """
    Extract message_id from:
    1. Forwarded messages (new forward_origin)
    2. t.me links
    """

    # ✅ Handle forwarded messages (UPDATED)
    origin = getattr(message, "forward_origin", None)

    if origin:
        chat = getattr(origin, "chat", None)
        msg_id = getattr(origin, "message_id", None)

        if chat and msg_id:
            if chat.id == client.db_channel.id:
                return msg_id

    # 🔗 Handle t.me links
    if message.text:
        match = re.match(r"https://t.me/(?:c/)?(.*)/(\d+)", message.text)

        if match:
            chan_id, msg_id = match.groups()
            msg_id = int(msg_id)

            # Private channel link (t.me/c/xxxx)
            if chan_id.isdigit():
                if f"-100{chan_id}" == str(client.db_channel.id):
                    return msg_id

            # Public username link
            else:
                if chan_id == client.db_channel.username:
                    return msg_id

    return 0