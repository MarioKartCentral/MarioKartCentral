from dataclasses import dataclass
import re

from common.data.commands import Command, save_to_command_log
from common.data.models import *

@save_to_command_log
@dataclass
class CreateFriendCodeCommand(Command[None]):
    player_id: int
    fc: str
    game: Game
    is_verified: bool
    is_primary: bool
    is_active: bool
    description: str | None
    is_privileged: bool

    async def handle(self, db_wrapper, s3_wrapper):
        is_primary = self.is_primary
        # make sure FC is in 0000-0000-0000 format
        match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", self.fc)
        if self.game != "mk8" and not match:
            raise Problem(f"FC {self.fc} for game {self.game} is in incorrect format", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT fc, is_primary FROM friend_codes WHERE player_id = ? AND game = ? AND is_active = ?",
                                  (self.player_id, self.game, True)) as cursor:
                rows = list(await cursor.fetchall())
                # if we have no fcs for this game before adding, is_primary should always be true
                if len(rows) == 0:
                    is_primary = True
                for row in rows:
                    row_fc, row_primary = row
                    if bool(row_primary) and self.is_primary:
                        raise Problem("Can only have 1 primary FC", status=400)
                    if row_fc == self.fc:
                        raise Problem("You are already using this FC", status=400)
                fc_count = len(rows)
                fc_limits = {"mk8dx": 1, "mkt": 1, "mkw": 4, "mk7": 1, "mk8": 1}
                if not self.is_privileged:
                    if fc_count >= fc_limits[self.game]:
                        raise Problem("Player is at maximum friend codes for this game", status=400)
                
            async with db.execute("SELECT id FROM friend_codes WHERE fc = ? AND game = ? AND (is_active = ? OR player_id = ?)", (self.fc, self.game, True, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Another player is currently using this friend code for this game", status=400)
            await db.execute("INSERT INTO friend_codes(player_id, game, fc, is_verified, is_primary, is_active, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (self.player_id, self.game, self.fc, self.is_verified, is_primary, self.is_active, self.description))
            await db.commit()

@save_to_command_log    
@dataclass
class EditFriendCodeCommand(Command[None]):
    player_id: int
    id: int
    fc: str | None
    is_primary: bool
    is_active: bool | None
    description: str | None

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT game, fc, is_active, is_primary FROM friend_codes WHERE id = ? AND player_id = ?", (self.id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("FC not found", status=404)
                game, curr_fc, curr_is_active, curr_is_primary = row
            if self.fc is not None:
                # make sure FC is in 0000-0000-0000 format
                match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", self.fc)
                if game != "mk8" and not match:
                    raise Problem("FC is in incorrect format", status=400)
                async with db.execute("SELECT id FROM friend_codes WHERE id != ? AND fc = ? AND game = ? AND (is_active = ? OR player_id = ?)", (self.id, self.fc, game, True, self.player_id)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("Another player is currently using this friend code for this game", status=400)
            fc = curr_fc if self.fc is None else self.fc
            is_active = curr_is_active if self.is_active is None else self.is_active
            if not is_active and self.is_primary:
                raise Problem("Inactive FCs cannot be primary", status=400)
            # if this FC is now primary, make all the other FCs this player has for that game non-primary
            if self.is_primary and not curr_is_primary:
                await db.execute("UPDATE friend_codes SET is_primary = 0 WHERE player_id = ? AND game = ? AND id != ?", (self.player_id, game, self.id))
            await db.execute("UPDATE friend_codes SET fc = ?, is_active = ?, description = ?, is_primary = ? WHERE id = ?", (fc, is_active, self.description, self.is_primary, self.id))
            await db.commit()

@save_to_command_log
@dataclass
class SetPrimaryFCCommand(Command[None]):
    id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM friend_codes WHERE id = ? AND player_id = ?", (self.id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("FC not found", status=404)
            await db.execute("UPDATE friend_codes SET is_primary = ? WHERE id != ? AND player_id = ?", (False, self.id, self.player_id))
            await db.execute("UPDATE friend_codes SET is_primary = ? WHERE id = ? AND player_id = ?", (True, self.id, self.player_id))
            await db.commit()