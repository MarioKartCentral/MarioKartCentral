from datetime import timedelta, timezone
from common.data.commands import Command, save_to_command_log
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *

@save_to_command_log
@dataclass
class RequestEditPlayerNameCommand(Command[None]):
    player_id: int
    name: str

    async def handle(self, db_wrapper: DBWrapper):
        if len(self.name) > 24:
            raise Problem("Player name must be 24 characters or less", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT name FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                curr_name = row[0]
                if curr_name == self.name:
                    raise Problem("Name must be different than current name", status=400)
            async with db.execute("SELECT date FROM player_name_edits WHERE player_id = ? AND date > ? AND approval_status != 'denied' LIMIT 1",
                                    (self.player_id, (datetime.now(timezone.utc)-timedelta(days=90)).timestamp())) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player has requested name change in the last 90 days", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO player_name_edits(player_id, old_name, new_name, date, approval_status) VALUES (?, ?, ?, ?, ?)", 
                             (self.player_id, curr_name, self.name.strip(), creation_date, "pending"))
            await db.commit()
                    
@dataclass
class ListPlayerNameRequestsCommand(Command[PlayerNameRequestList]):
    filter: PlayerNameRequestFilter

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            filter = self.filter
            limit = 20
            offset = 0
            if filter.page is not None:
                offset = (filter.page - 1) * limit

            name_requests: list[PlayerNameRequest] = []
            request_query = """FROM player_name_edits r
                                JOIN players p ON r.player_id = p.id
                                LEFT JOIN players p2 ON r.handled_by = p2.id
                                WHERE r.approval_status = ? ORDER BY r.date DESC"""
            async with db.execute(f"""SELECT p.id, p.country_code, r.id, r.old_name, r.new_name, r.date, r.approval_status, r.handled_by, p2.name, p2.country_code
                                  {request_query} LIMIT ? OFFSET ?""", (filter.approval_status, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_country, request_id, old_name, new_name, date, approval_status, handled_by_id, handled_by_name, handled_by_country = row
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country)
                    name_requests.append(PlayerNameRequest(request_id, player_id, player_country, old_name, new_name, date, approval_status, handled_by))

            count_query = f"SELECT COUNT(*) {request_query}"
            async with db.execute(count_query, (filter.approval_status,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                request_count = row[0]

            page_count = int(request_count / limit) + (1 if request_count % limit else 0)

        return PlayerNameRequestList(name_requests, request_count, page_count)
    
@save_to_command_log
@dataclass
class ApprovePlayerNameRequestCommand(Command[None]):
    request_id: int
    mod_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, new_name FROM player_name_edits WHERE id = ?", (self.request_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Name edit request not found", status=400)
                player_id, name = row
            await db.execute("UPDATE players SET name = ? WHERE id = ?", (name, player_id))
            await db.execute("UPDATE player_name_edits SET approval_status = 'approved', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id))
            await db.commit()

@save_to_command_log
@dataclass
class DenyPlayerNameRequestCommand(Command[None]):
    request_id: int
    mod_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE player_name_edits SET approval_status = 'denied', handled_by = ? WHERE id = ?", (self.mod_player_id, self.request_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Name edit request not found", status=404)
                await db.commit()