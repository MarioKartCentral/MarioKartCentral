from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@dataclass
class RequestVerificationCommand(Command[None]):
    player_id: int | None
    friend_code_ids: list[int]
    verify_player: bool # whether to request verification for the player themselves or just their FCs

    async def handle(self, db_wrapper: DBWrapper):
        if self.player_id is None:
            raise Problem("Must be registered as a player to request verification", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_verified FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", status=404)
                player_is_verified = bool(row[0])

                if self.verify_player and player_is_verified:
                    raise Problem("Player is already verified", status=400)
                
                if not self.verify_player and len(self.friend_code_ids) == 0:
                    raise Problem("At least one friend code must be provided if player is not requesting verification", status=400)
                
            for fc_id in self.friend_code_ids:
                async with db.execute("SELECT type, fc, is_verified, is_active FROM friend_codes WHERE id = ? AND player_id = ?", (fc_id, self.player_id)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem(f"Friend code with ID {fc_id} not found", status=404)
                    fc_type, fc_fc, fc_is_verified, fc_is_active = row

                    if bool(fc_is_verified):
                        raise Problem(f"FC with ID {fc_id} ({fc_fc}) is already verified", status=400)
                    if not bool(fc_is_active):
                        raise Problem(f"FC with ID {fc_id} ({fc_fc}) is inactive", status=400)
                    
                    # For now we should only allow players to verify their Switch FCs
                    allowed_fc_types = ["switch"]
                    if fc_type not in allowed_fc_types:
                        raise Problem(f"FC with ID {fc_id} ({fc_fc})'s type cannot be verified ({fc_type})", status=400)
                    
                async with db.execute("SELECT id FROM friend_code_verification_requests WHERE fc_id = ? AND approval_status = 'pending'", (fc_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem(f"Friend code with ID {fc_id} ({fc_fc}) already has a pending verification request", status=400)
                    
            now = int(datetime.now(timezone.utc).timestamp())
            if self.verify_player:
                async with db.execute("SELECT id FROM player_verification_requests WHERE player_id = ? AND approval_status = 'pending'", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem("Player already has a pending verification request", status=400)
                
                await db.execute("INSERT INTO player_verification_requests(player_id, date, approval_status) VALUES(?, ?, 'pending')", (self.player_id, now))

            await db.executemany("INSERT INTO friend_code_verification_requests(fc_id, date, approval_status) VALUES(?, ?, 'pending')",
                                 [(fc_id, now) for fc_id in self.friend_code_ids])
            await db.commit()