from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List
import json
from common.auth import team_roles

from common.data.commands import Command, save_to_command_log
from common.data.models import *

@dataclass
class GetNotificationsCommand(Command[list[Notification]]):
    user_id: int
    data: NotificationFilter

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data

        where_clauses: list[str] = ['user_id = ?']
        where_params: list[Any]  = [self.user_id]

        if data.is_read is not None:
            where_clauses.append('is_read = ?')
            where_params.append(data.is_read)
        if data.type is not None:
            try:
                types = list(map(int, data.type.split(','))) # convert types to list of ints
                type_query = ['type = ?'] * len(types)
                where_clauses.append(f"({' OR '.join(type_query)})")
                where_params += types
            except Exception as e:
                raise Problem('Bad type query', detail=str(e), status=400)
        if data.before is not None:
            try:
                where_clauses.append('created_date < ?')
                where_params.append(int(data.before))
            except Exception as e:
                raise Problem('Bad before date query', detail=str(e),  status=400)
        if data.after is not None:
            try:
                where_clauses.append('created_date > ?')
                where_params.append(data.after)
            except Exception as e:
                raise Problem('Bad after date query', detail=str(e), status=400)

        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(f"""
                SELECT id, type, content_id, content_args, link, created_date, is_read FROM notifications
                WHERE {' AND '.join(where_clauses)}""", tuple(where_params)) as cursor:

                return [Notification(row[0], row[1], int(row[2]), json.loads(row[3]), row[4], row[5], bool(row[6])) for row in await cursor.fetchall()]

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

@save_to_command_log
@dataclass
class DispatchNotificationCommand(Command[int]):
    user_ids: list[int]
    content_id: int
    content_args: list[str]
    link: str | None
    notification_type: int = 0

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            created_date = int(datetime.now(timezone.utc).timestamp())
            row_args = [(user_id, self.notification_type, self.content_id, json.dumps(self.content_args), self.link, created_date) for user_id in self.user_ids]

            async with await db.executemany("INSERT INTO notifications(user_id, type, content_id, content_args, link, created_date) VALUES (?, ?, ?, ?, ?, ?)", row_args) as cursor:
                count = cursor.rowcount
                if count > 0:
                    await db.commit()

            return count
        
@dataclass
class GetFieldFromTableCommand(Command[str]):
    query: str
    where_params: Any

    async def handle(self, db_wrapper, s3_wrapper) -> str:
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(self.query, self.where_params) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Failed to get field from table", status=500)

                return row[0]

@dataclass
class GetRowFromTableCommand(Command[List[Any]]):
    query: str
    where_params: Any

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute(self.query, self.where_params) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Failed to get row from table", status=500)

                return [i for i in row]

@dataclass
class GetTeamManagerAndLeaderUserIdsCommand(Command[List[int]]):
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            user_ids: List[int] = []
            async with db.execute("""SELECT u.id FROM players p
                JOIN users u ON u.player_id = p.id
                JOIN user_team_roles ur ON ur.user_id = u.id
                JOIN team_roles tr ON tr.id = ur.role_id
                WHERE ur.team_id = ? AND (tr.name = ? OR tr.name = ?)""", (self.team_id, team_roles.MANAGER, team_roles.LEADER)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    user_ids.append(row[0])
            return user_ids