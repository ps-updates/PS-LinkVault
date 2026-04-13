# Improved ScheduleManager by @Mak0912 (TG)

import datetime
import tzlocal
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.errors import FloodWait

from info import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database import save_delete_task, delete_saved_task, get_all_delete_tasks


class ScheduleManager:
    def __init__(self) -> None:
        self.timezone = tzlocal.get_localzone()
        self.scheduler = AsyncIOScheduler(
            timezone=self.timezone,
            misfire_grace_time=10,  # increased safety window
            coalesce=True,         # merge missed jobs
            max_instances=3        # prevent spam execution
        )

    async def start(self) -> None:
        """Start scheduler safely"""
        if not self.scheduler.running:
            self.scheduler.start()

    # 🔥 SAFE DELETE (handles floodwait + errors)
    async def _safe_delete(self, client: Client, chat_id: int, message_ids: list[int]):
        chunk_size = 100

        for i in range(0, len(message_ids), chunk_size):
            chunk = message_ids[i:i + chunk_size]

            try:
                await client.delete_messages(chat_id=chat_id, message_ids=chunk)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.delete_messages(chat_id=chat_id, message_ids=chunk)

            except Exception:
                continue  # skip bad chunk instead of crashing

    async def delete_messages(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        base64_file_link: str,
        task_id: str = None
    ) -> None:

        # ✅ delete safely
        await self._safe_delete(client, chat_id, message_ids)

        # ✅ send retrieve button (safe)
        try:
            retrieve_button = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🗂 Retrieve Deleted File(s)",
                    url=f"https://t.me/{client.me.username}?start={base64_file_link}"
                )]
            ])

            await client.send_message(
                chat_id=chat_id,
                text=Config.AUTO_DEL_SUCCESS_MSG,
                reply_markup=retrieve_button,
            )

        except Exception:
            pass  # don't crash if message fails

        # ✅ cleanup db
        if task_id:
            await delete_saved_task(task_id)

    async def schedule_delete(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        delete_n_seconds: int,
        base64_file_link: str
    ) -> None:

        run_time = datetime.datetime.now(tz=self.timezone) + datetime.timedelta(seconds=delete_n_seconds)

        # 🔥 Better unique ID (no collision risk)
        task_id = f"{chat_id}:{message_ids[0]}:{int(datetime.datetime.utcnow().timestamp()*1000)}"

        # ❌ prevent duplicate jobs
        if self.scheduler.get_job(task_id):
            return

        self.scheduler.add_job(
            func=self.delete_messages,
            trigger="date",
            run_date=run_time,
            args=[client, chat_id, message_ids, base64_file_link, task_id],
            id=task_id,
            replace_existing=True
        )

        await save_delete_task(
            chat_id,
            message_ids,
            base64_file_link,
            run_time.isoformat(),
            task_id
        )

    async def restore_pending_deletes(self, client: Client) -> None:
        """Restore scheduled deletes from DB on startup"""

        pending = await get_all_delete_tasks()
        current_time = datetime.datetime.now(tz=self.timezone)

        for task in pending:
            try:
                run_time = datetime.datetime.fromisoformat(task["run_time"])

                if run_time < current_time:
                    # 🔥 missed job → execute instantly
                    await self.delete_messages(
                        client,
                        task["chat_id"],
                        task["message_ids"],
                        task["base64_file_link"],
                        task["_id"],
                    )
                    continue

                # 🔥 avoid duplicate scheduling
                if self.scheduler.get_job(task["_id"]):
                    continue

                self.scheduler.add_job(
                    func=self.delete_messages,
                    trigger="date",
                    run_date=run_time,
                    args=[
                        client,
                        task["chat_id"],
                        task["message_ids"],
                        task["base64_file_link"],
                        task["_id"]
                    ],
                    id=task["_id"],
                    replace_existing=True
                )

            except Exception:
                continue


schedule_manager = ScheduleManager()