# Adapted from: https://github.com/zawsq/Teleshare/blob/main/bot/utilities/schedule_manager.py
# Modified & extended by: @Mak0912 (TG)


import datetime
import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from info import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database import save_delete_task, delete_saved_task, get_all_delete_tasks

class ScheduleManager:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(
            timezone=tzlocal.get_localzone(),
            misfire_grace_time=5,
        )

    async def start(self) -> None:
        """
        Starts the scheduler.
        """
        self.scheduler.start()


    async def delete_messages(self, client: Client, chat_id: int, message_ids: list[int], base64_file_link: str, task_id: str = None) -> None:
        chunk_size = 100
        chunked_ids = [message_ids[i:i+chunk_size] for i in range(0, len(message_ids), chunk_size)]

        for chunk in chunked_ids:
            await client.delete_messages(chat_id=chat_id, message_ids=chunk)

        retrieve_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗂 Retrieve Deleted File(s)", url=f"https://t.me/{client.me.username}?start={base64_file_link}")]
        ])
        await client.send_message(
            chat_id=chat_id,
            text=Config.AUTO_DEL_SUCCESS_MSG,
            reply_markup=retrieve_button,
        )

        if task_id:
            await delete_saved_task(task_id)

    async def schedule_delete(self, client: Client, chat_id: int, message_ids: list[int], delete_n_seconds: int, base64_file_link: str) -> None:
        run_time = datetime.datetime.now(tz=tzlocal.get_localzone()) + datetime.timedelta(seconds=delete_n_seconds)
        task_id = f"{chat_id}_{message_ids[0]}_{datetime.datetime.utcnow().timestamp()}"

        self.scheduler.add_job(
            func=self.delete_messages,
            trigger="date",
            run_date=run_time,
            args=[client, chat_id, message_ids, base64_file_link, task_id],
            id=task_id,
        )

        await save_delete_task(
            chat_id,
            message_ids,
            base64_file_link,
            run_time.isoformat(),
            task_id
        )

    async def restore_pending_deletes(self, client: Client) -> None:
        """Load all scheduled deletes from MongoDB on bot startup."""
        pending = await get_all_delete_tasks()
        for task in pending:
            run_time = datetime.datetime.fromisoformat(task["run_time"])
            current_time = datetime.datetime.now(tz=tzlocal.get_localzone())

            if run_time < current_time:
                # task missed while bot was offline — delete immediately
                await self.delete_messages(
                    client,
                    chat_id=task["chat_id"],
                    message_ids=task["message_ids"],
                    base64_file_link=task["base64_file_link"],
                    task_id=task["_id"],
                )
                continue

            self.scheduler.add_job(
                func=self.delete_messages,
                trigger="date",
                run_date=run_time,
                args=[client, task["chat_id"], task["message_ids"], task["base64_file_link"], task["_id"]],
                id=task["_id"],
            )
            
schedule_manager = ScheduleManager()
