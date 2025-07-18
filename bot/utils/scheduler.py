import asyncio
from info import Config

def get_readable_time(seconds: int) -> str:
    """
    Convert seconds into a readable format: days:hours:minutes:seconds
    """
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]

    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "

    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

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
