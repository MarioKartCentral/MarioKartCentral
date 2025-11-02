from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@dataclass
class UpdatePlayerNotesCommand(Command[None]):
    player_id: int
    notes: str
    edited_by: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='player_notes') as db:
            date = int(datetime.now(timezone.utc).timestamp())
            query = """INSERT INTO player_notes (player_id, notes, edited_by, date) VALUES (?, ?, ?, ?) 
                ON CONFLICT (player_id) DO 
                UPDATE SET notes = excluded.notes, edited_by = excluded.edited_by, date = excluded.date"""
            params = (self.player_id, self.notes, self.edited_by, date)
            if not self.notes:
                query = "DELETE FROM player_notes WHERE player_id = ?"
                params = (self.player_id,)

            async with db.execute(query, params) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Player not found", status=404)
                await db.commit()