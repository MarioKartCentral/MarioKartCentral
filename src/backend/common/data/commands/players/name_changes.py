from datetime import timedelta, timezone
from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class RequestEditPlayerNameCommand(Command[None]):
    player_id: int
    name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                curr_name = row[0]
                if curr_name == self.name:
                    raise Problem("Name must be different than current name", status=400)
            async with db.execute("SELECT date FROM player_name_edit_requests WHERE player_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                    (self.player_id, (datetime.now(timezone.utc)-timedelta(days=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player has requested name change in the last 90 days", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO player_name_edit_requests(player_id, name, date, approval_status) VALUES (?, ?, ?, ?)", 
                             (self.player_id, self.name, creation_date, "pending"))
            await db.commit()
                    
@dataclass
class ListPlayerNameRequestsCommand(Command[list[PlayerNameRequest]]):
    approval_status: Approval

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            name_requests: list[PlayerNameRequest] = []
            async with db.execute("""SELECT p.id, p.name, p.country_code, r.id, r.name, r.date, r.approval_status
                                    FROM player_name_edit_requests r
                                    JOIN players p ON r.player_id = p.id
                                    WHERE r.approval_status = ?""", (self.approval_status,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, player_country, request_id, request_name, date, approval_status = row
                    name_requests.append(PlayerNameRequest(request_id, player_id, player_name, player_country, request_name, date, approval_status))
        return name_requests
    
@save_to_command_log
@dataclass
class ApprovePlayerNameRequestCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, name FROM player_name_edit_requests WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Name edit request not found", status=400)
                player_id, name = row
            await db.execute("UPDATE players SET name = ? WHERE id = ?", (name, player_id))
            await db.execute("UPDATE player_name_edit_requests SET approval_status = 'approved' WHERE id = ?", (self.request_id,))
            await db.commit()

@save_to_command_log
@dataclass
class DenyPlayerNameRequestCommand(Command[None]):
    request_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE player_name_edit_requests SET approval_status = 'denied' WHERE id = ?", (self.request_id,)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Name edit request not found", status=404)
                await db.commit()