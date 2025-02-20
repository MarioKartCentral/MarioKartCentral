from common.data.commands import Command, save_to_command_log
from common.data.models import *
from datetime import datetime, timezone

@save_to_command_log
@dataclass
class UpdatePlayerNotesCommand(Command[None]):
    player_id: int
    notes: str
    edited_by: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
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