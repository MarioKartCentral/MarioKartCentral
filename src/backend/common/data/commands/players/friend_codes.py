from dataclasses import dataclass
import re

from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@dataclass
class CreateFriendCodeCommand(Command[None]):
    player_id: int
    fc: str
    type: FriendCodeType
    is_verified: bool
    is_primary: bool
    is_active: bool
    description: str | None
    is_privileged: bool

    async def handle(self, db_wrapper: DBWrapper):
        is_primary = self.is_primary
        # make sure FC is in 0000-0000-0000 format
        match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", self.fc)
        if self.type != "nnid" and not match:
            raise Problem(f"FC {self.fc} of type {self.type} is in incorrect format", status=400)
        if self.type == "nnid" and len(self.fc) > 16:
            raise Problem("NNIDs must be 16 characters or less", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT fc, is_primary FROM friend_codes WHERE player_id = ? AND type = ? AND is_active = ?",
                                  (self.player_id, self.type, True)) as cursor:
                rows = list(await cursor.fetchall())
                # if we have no fcs of this type before adding, is_primary should always be true
                if len(rows) == 0:
                    is_primary = True
                for row in rows:
                    row_fc, row_primary = row
                    if bool(row_primary) and self.is_primary:
                        raise Problem("Can only have 1 primary FC", status=400)
                    if row_fc == self.fc:
                        raise Problem("You are already using this FC", status=400)
                fc_count = len(rows)
                fc_limits: dict[FriendCodeType, int] = {"switch": 1, "mkt": 1, "mkw": 4, "3ds": 1, "nnid": 1}
                if not self.is_privileged:
                    if fc_count >= fc_limits[self.type]:
                        raise Problem("Player is at maximum friend codes for this category", status=400)
                
            async with db.execute("SELECT id FROM friend_codes WHERE fc = ? AND type = ? AND (is_active = ? OR player_id = ?)", (self.fc, self.type, True, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Another player is currently using this friend code for this category", status=400)
            now = int(datetime.now(timezone.utc).timestamp())
            async with db.execute("INSERT INTO friend_codes(player_id, type, fc, is_verified, is_primary, is_active, description, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (self.player_id, self.type, self.fc, self.is_verified, is_primary, self.is_active, self.description, now)) as cursor:
                fc_id = cursor.lastrowid
            await db.execute("INSERT INTO friend_code_edits(fc_id, new_fc, date) VALUES(?, ?, ?)", (fc_id, self.fc, now)) # log friend code creation
            await db.commit()

@dataclass
class EditFriendCodeCommand(Command[None]):
    player_id: int
    id: int
    fc: str | None
    is_primary: bool
    is_active: bool | None
    description: str | None
    mod_player_id: int | None

    async def handle(self, db_wrapper: DBWrapper):
        
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT type, fc, is_active, is_primary FROM friend_codes WHERE id = ? AND player_id = ?", (self.id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("FC not found", status=404)
                type, curr_fc, curr_is_active, curr_is_primary = row
            if type == "nnid" and self.fc and len(self.fc) > 16:
                raise Problem("NNIDs must be 16 characters or less", status=400)
            if self.fc is not None:
                # make sure FC is in 0000-0000-0000 format
                match = re.fullmatch(r"\d{4}-\d{4}-\d{4}", self.fc)
                if type != "nnid" and not match:
                    raise Problem("FC is in incorrect format", status=400)
                async with db.execute("SELECT id FROM friend_codes WHERE id != ? AND fc = ? AND type = ? AND (is_active = ? OR player_id = ?)", (self.id, self.fc, type, True, self.player_id)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("Another player is currently using this friend code for this category", status=400)
            fc = curr_fc if self.fc is None else self.fc
            is_active = curr_is_active if self.is_active is None else self.is_active
            if not is_active and self.is_primary:
                raise Problem("Inactive FCs cannot be primary", status=400)
            # if this FC is now primary, make all the other FCs this player has for that type non-primary
            if self.is_primary and not curr_is_primary:
                await db.execute("UPDATE friend_codes SET is_primary = 0 WHERE player_id = ? AND type = ? AND id != ?", (self.player_id, type, self.id))
            await db.execute("UPDATE friend_codes SET fc = ?, is_active = ?, description = ?, is_primary = ? WHERE id = ?", (fc, is_active, self.description, self.is_primary, self.id))
            # log fc edit if a mod changes it
            if self.mod_player_id:
                now = int(datetime.now(timezone.utc).timestamp())
                old_fc = curr_fc if curr_fc != fc else None
                new_fc = fc if curr_fc != fc else None
                is_active = is_active if curr_is_active != is_active else None
                await db.execute("INSERT INTO friend_code_edits(fc_id, old_fc, new_fc, is_active, handled_by, date) VALUES(?, ?, ?, ?, ?, ?)",
                                 (self.id, old_fc, new_fc, is_active, self.mod_player_id, now))
            await db.commit()

@dataclass
class SetPrimaryFCCommand(Command[None]):
    id: int
    player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM friend_codes WHERE id = ? AND player_id = ?", (self.id, self.player_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("FC not found", status=404)
            await db.execute("UPDATE friend_codes SET is_primary = ? WHERE id != ? AND player_id = ?", (False, self.id, self.player_id))
            await db.execute("UPDATE friend_codes SET is_primary = ? WHERE id = ? AND player_id = ?", (True, self.id, self.player_id))
            await db.commit()

@dataclass
class ListFriendCodeEditsCommand(Command[FriendCodeEditList]):
    filter: FriendCodeEditFilter

    async def handle(self, db_wrapper: DBWrapper):
        filter = self.filter

        limit:int = 50
        offset:int = 0

        if filter.page is not None:
            offset = (filter.page - 1) * limit

        edit_query = """FROM friend_code_edits e
                        JOIN friend_codes f ON e.fc_id = f.id
                        JOIN players p ON f.player_id = p.id
                        LEFT JOIN players p2 ON e.handled_by = p2.id"""
        
        async with db_wrapper.connect() as db:
            edits: list[FriendCodeEdit] = []
            async with db.execute(f"""SELECT e.id, e.old_fc, e.new_fc, e.is_active, e.date,
                                        f.id, f.type, f.fc, f.is_verified, f.is_primary, f.is_active,
                                        f.description, f.creation_date, p.id, p.name, p.country_code, p.is_banned, p.is_verified,
                                        p2.id, p2.name, p2.country_code, p2.is_banned, p2.is_verified
                                        {edit_query} ORDER BY e.date DESC LIMIT ? OFFSET ?
                                  """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (edit_id, old_fc, new_fc, edit_active, edit_date, fc_id, fc_type, fc_fc, is_verified, is_primary, is_active,
                    description, creation_date, player_id, player_name, player_country, player_banned, player_verified, handled_by_id, handled_by_name, 
                    handled_by_country, handled_by_banned, handled_by_verified) = row
                    player = PlayerBasic(player_id, player_name, player_country, bool(player_banned), bool(player_verified))
                    fc = FriendCode(fc_id, fc_fc, fc_type, player_id, is_verified, is_primary, creation_date, description, is_active)
                    handled_by = None
                    if handled_by_id:
                        handled_by = PlayerBasic(handled_by_id, handled_by_name, handled_by_country, bool(handled_by_banned), bool(handled_by_verified))
                    edit = FriendCodeEdit(edit_id, old_fc, new_fc, edit_active, edit_date, fc, player, handled_by)
                    edits.append(edit)
        
            count_query = f"""SELECT COUNT(*) FROM (SELECT DISTINCT e.id {edit_query})"""
            page_count: int = 0
            count: int = 0
            async with db.execute(count_query) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = row[0]
            
            page_count = int(count / limit) + (1 if count % limit else 0)
            return FriendCodeEditList(edits, count, page_count)
