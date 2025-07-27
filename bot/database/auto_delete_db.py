from .connection import db
from typing import List, Union
from datetime import datetime

collection = db["schedule_delete"]

async def save_delete_task(
    chat_id: Union[int, str],
    message_ids: List[int],
    base64_file_link: str,
    run_time: Union[str, datetime],
    task_id: str
):
    await collection.insert_one({
        "_id": task_id,
        "chat_id": chat_id,
        "message_ids": message_ids,
        "base64_file_link": base64_file_link,
        "run_time": run_time if isinstance(run_time, str) else run_time.isoformat(),
    })

async def delete_saved_task(task_id: str):
    await collection.delete_one({"_id": task_id})

async def get_all_delete_tasks() -> List[dict]:
    return await collection.find({}).to_list(length=None)
