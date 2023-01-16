from api.db import connect_db
from datetime import datetime, timezone
from typing import List

# When dispatching a notification, use one of the following keys (or corresponding integer) 
# below for the notif_type parameter.
notif_types = {
    "Info": 0,
}

async def _notify(content: str, user_ids: List[int], notif_type: int = 0) -> int:
    """ Helper to dispatch notifications to a list of user ids.
        Returns the number of rows added to the 'notifications' table.
        You shouldn't call this function directly, but rather
        call either notify_one, notify_many, or notify_everyone.
    """

    async with connect_db() as db:
        inserted_row = await db.execute_insert("INSERT INTO notification_content(content) VALUES (?)", (content, ))
        content_id = inserted_row[0]
        await db.commit()

        created_date = datetime.now(timezone.utc).timestamp()
        content_is_shared = len(user_ids) > 1
        row_args = [(user_id, notif_type, content_id, created_date, content_is_shared) for user_id in user_ids]

        async with await db.executemany(
            "INSERT INTO notifications(user_id, type, content_id, created_date, content_is_shared) VALUES (?, ?, ?, ?, ?)",
            row_args) as cursor:
            
            count = cursor.rowcount
            if count > 0:
                await db.commit()

    return count

async def notify_one(content: str, user_id: int, notif_type: int = 0) -> int:
    """ Dispatch a notification to a single user """
    return await _notify(content, [user_id], notif_type)

async def notify_many(content: str, user_ids: List[int], notif_type: int = 0) -> int:
    """ Dispatch notifications to a list of users with the same content and type for everyone """
    return await _notify(content, user_ids, notif_type)
    
async def notify_everyone(content: str, notif_type: int = 0) -> int:
    """ Dispatch notifications to all users with the same content and type for everyone """
    async with connect_db() as db:
        async with db.execute("SELECT id FROM users") as cursor:
            user_ids = [row[0] for row in await cursor.fetchall()]
    return await _notify(content, user_ids, notif_type)