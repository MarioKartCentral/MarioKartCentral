from dataclasses import dataclass
from datetime import datetime, timezone
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *

@dataclass
class InvitePlayerCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int
    is_bagger_clause: bool

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id, game, approval_status FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id, game, approval_status = row
                if approval_status != "approved":
                    raise Problem("Cannot invite players to roster if it is not approved", status=400)
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
                if self.is_bagger_clause and game != "mkw":
                    raise Problem("Cannot invite players as baggers for games other than MKW", status=400)
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
            fc_type = game_fc_map[game]
            async with db.execute("SELECT id FROM friend_codes WHERE type = ? AND player_id = ? AND is_active = ?", (fc_type, self.player_id, True)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player has no friend codes for this game", status=400)
            async with db.execute("SELECT id FROM team_members WHERE player_id = ? AND roster_id = ? AND leave_date IS ? AND is_bagger_clause = ?", 
                                  (self.player_id, self.roster_id, None, self.is_bagger_clause)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("Player is already on this roster", status=400)
            async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE player_id = ? AND roster_id = ? AND approval_status != 'approved'", (self.player_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                num_invites = row[0]
                if num_invites > 0:
                    raise Problem("Player has already been invited", status=400)
            if self.is_bagger_clause:
                bagger_count = 0
                async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE roster_id = ? AND approval_status != 'approved' AND is_bagger_clause = 1", (self.roster_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    bagger_count += row[0]
                async with db.execute("SELECT COUNT(id) FROM team_members WHERE roster_id = ? AND leave_date IS NULL AND is_bagger_clause = 1", (self.roster_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    bagger_count += row[0]
                if bagger_count >= 2:
                    raise Problem("Rosters may only have 2 bag-claused players at once", status=400)
            creation_date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO team_transfers(player_id, roster_id, date, is_bagger_clause, is_accepted, approval_status) VALUES (?, ?, ?, ?, ?, ?)", 
                             (self.player_id, self.roster_id, creation_date, self.is_bagger_clause, False, "pending"))
            await db.commit()

@dataclass
class DeleteInviteCommand(Command[None]):
    player_id: int
    roster_id: int
    team_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT team_id FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Roster not found", status=404)
                roster_team_id = row[0]
                if int(roster_team_id) != self.team_id:
                    raise Problem("Roster is not part of specified team", status=400)
            async with db.execute("DELETE FROM team_transfers WHERE player_id = ? AND roster_id = ?", (self.player_id, self.roster_id)) as cursor:
                rowcount = cursor.rowcount
                if rowcount == 0:
                    raise Problem("Invite not found", status=404)
            await db.commit()

@dataclass
class AcceptInviteCommand(Command[None]):
    invite_id: int
    roster_leave_id: int | None
    player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT r.game, i.player_id, i.is_bagger_clause FROM team_transfers i JOIN team_rosters r ON i.roster_id = r.id WHERE i.id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                game, invite_player_id, is_bagger_clause = row
                if self.player_id != invite_player_id:
                    raise Problem("Cannot accept invite for another player", status=400)
            # make sure that we are actually in the roster we're leaving
            if self.roster_leave_id:
                async with db.execute("SELECT id FROM team_members WHERE roster_id = ? AND player_id = ? AND leave_date IS ? AND is_bagger_clause = ?",
                                      (self.roster_leave_id, self.player_id, None, is_bagger_clause)) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise Problem("Player is not registered for the roster they are leaving", status=400)
            # make sure we have at least one FC for the game of the roster that we are accepting an invite for
            fc_type = game_fc_map[game]
            async with db.execute("SELECT count(id) FROM friend_codes WHERE player_id = ? AND type = ?", (self.player_id, fc_type)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                fc_count = row[0]
                if fc_count == 0:
                    raise Problem("Player does not have any friend codes for this roster's game", status=400)
            now = int(datetime.now(timezone.utc).timestamp())
            # we do not move the player to the team's roster just yet, just mark it as accepted, a moderator must approve the transfer
            await db.execute("UPDATE team_transfers SET roster_leave_id = ?, is_accepted = ?, date = ? WHERE id = ?", (self.roster_leave_id, True, now, self.invite_id))
            await db.commit()

@dataclass
class DeclineInviteCommand(Command[None]):
    invite_id: int
    player_id: int
    is_privileged: bool = False

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            # check if invite exists and to make sure we're the same player as the invite
            async with db.execute("SELECT player_id FROM team_transfers WHERE id = ?", (self.invite_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("No invite found", status=404)
                invite_player_id = row[0]
                if self.player_id != invite_player_id and not self.is_privileged:
                    raise Problem("Cannot decline invite for another player", status=400)
            await db.execute("DELETE FROM team_transfers WHERE id = ?", (self.invite_id,))
            await db.commit()
