import asyncio
from info import Config

async def schedule_auto_delete(messages, client, notice_msg):
    """
    Waits for AUTO_DELETE_TIME seconds and deletes given messages.
    Then edits the notice message with AUTO_DEL_SUCCESS_MSG.
    """
    await asyncio.sleep(Config.AUTO_DELETE_TIME)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"❌ Failed to delete message {msg.id}: {e}")

    try:
        await notice_msg.edit_text(Config.AUTO_DEL_SUCCESS_MSG)
    except Exception as e:
        print(f"❌ Failed to edit notice message: {e}")
