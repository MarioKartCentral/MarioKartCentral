from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

from common.data.commands import Command
from common.data.models import *


@dataclass
class GetNotificationsCommand(Command[List[Notification]]):
    user_id: int
    data: NotificationFilter

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data

        where_clauses: list[str] = ['n.user_id = ?']
        where_params: list[Any]  = [self.user_id]

        if data.is_read is not None:
            where_clauses.append('n.is_read = ?')
            where_params.append(data.is_read)
        if data.type is not None:
            try:
                types = list(map(int, data.type.split(','))) # convert types to list of ints
                type_query = ['n.type = ?'] * len(types)
                where_clauses.append(f"({' OR '.join(type_query)})")
                where_params += types
            except Exception as e:
                raise Problem('Bad type query', detail=str(e), status=400)
        if data.before is not None:
            try:
                where_clauses.append('n.created_date < ?')
                where_params.append(int(data.before))
            except Exception as e:
                raise Problem('Bad before date query', detail=str(e),  status=400)
        if data.after is not None:
            try:
                where_clauses.append('n.created_date > ?')
                where_params.append(data.after)
            except Exception as e:
                raise Problem('Bad after date query', detail=str(e), status=400)

        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(f"""
                SELECT n.id, n.type, c.content, n.created_date, n.is_read FROM notifications n
                JOIN notification_content c ON n.content_id = c.id
                WHERE {' AND '.join(where_clauses)}""", tuple(where_params)) as cursor:

                return [Notification(row[0], row[1], row[2], row[3], bool(row[4])) for row in await cursor.fetchall()]

@dataclass
class MarkOneNotificationAsReadCommand(Command[int]):
    id: int
    user_id: int
    data: MarkAsReadRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        is_read = 1 if self.data.is_read else 0
        notification_id = self.id
        user_id = self.user_id

        async with db_wrapper.connect() as db:
            async with db.execute("""
                UPDATE notifications SET is_read = ?
                WHERE id = ? AND user_id = ?""", (is_read, notification_id, user_id)) as cursor:

                if cursor.rowcount == 1:
                    await db.commit()
                    return cursor.rowcount

            # either the notification does not exist, or the request user_id does not match notif user_id
            async with db.execute("SELECT EXISTS (SELECT 1 FROM notifications WHERE id = ?)", (notification_id, )) as cursor:
                row = await cursor.fetchone()
                notification_exists = row is not None and bool(row[0])

                if notification_exists:
                    raise Problem('User does not have permission', status=401)
                raise Problem('Unknown notification', status=404)

@dataclass
class MarkAllNotificationsAsReadCommand(Command[int]):
    user_id: int
    data: MarkAsReadRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        is_read = 1 if self.data.is_read else 0
        user_id = self.user_id

        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE notifications SET is_read = ? WHERE user_id = ?", (is_read, user_id)) as cursor:
                count = cursor.rowcount
                if count > 0:
                    await db.commit()
                return count
            
@dataclass
class GetUnreadNotificationsCountCommand(Command[int]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT COUNT (*) FROM notifications WHERE user_id = ? AND is_read = 0""", (self.user_id, )) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Unable to fetch unread notifications count")
                return int(row[0])

@dataclass
class DispatchNotificationsCommand(Command[int]):
    """
    Dispatch a notification to one or more users, and returns the numbers of notifications that were sent.

    content:
        The notification message to send. All users will be notified with the same content.

    notification_type:
        The type of the notification.

    user_ids:
        A list of one or more user IDs to dispatch to.
    """
    content: str
    user_ids: List[int]
    notification_type: int = 0

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            inserted_row = await db.execute_insert("INSERT INTO notification_content(content) VALUES (?)", (self.content, ))
            if inserted_row is None:
                raise Problem('Failed to insert notification content to db')
            
            content_id = int(inserted_row[0])
            await db.commit()

            user_ids = self.user_ids
            created_date = int(datetime.utcnow().timestamp())
            content_is_shared = int(len(user_ids) > 1)
            row_args = [(user_id, self.notification_type, content_id, created_date, content_is_shared) for user_id in user_ids]

            async with await db.executemany("INSERT INTO notifications(user_id, type, content_id, created_date, content_is_shared) VALUES (?, ?, ?, ?, ?)", row_args) as cursor:
                count = cursor.rowcount
                if count > 0:
                    await db.commit()

            return count