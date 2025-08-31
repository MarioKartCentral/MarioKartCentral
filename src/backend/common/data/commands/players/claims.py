from common.data.commands import Command, save_to_command_log
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@save_to_command_log
@dataclass
class ClaimPlayerCommand(Command[None]):
    player_id: int
    claimed_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Claiming player not found", status=404)
            async with db.execute("SELECT is_shadow FROM players WHERE id = ?", (self.claimed_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Claimed player not found", status=404)
                is_shadow = bool(row[0])
                if not is_shadow:
                    raise Problem("Cannot claim a non-shadow player", status=400)
            async with db.execute("SELECT id FROM player_claims WHERE player_id = ? AND claimed_player_id = ? AND approval_status = ?",
                                  (self.player_id, self.claimed_player_id, "pending")) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("You already have a pending claim for this player", status=400)
            date = int(datetime.now(timezone.utc).timestamp())
            await db.execute("INSERT INTO player_claims(player_id, claimed_player_id, date, approval_status) VALUES(?, ?, ?, ?)",
                             (self.player_id, self.claimed_player_id, date, "pending"))
            await db.commit()

@save_to_command_log
@dataclass
class ApprovePlayerClaimCommand(Command[tuple[int, int, str]]):
    claim_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            # get the user id of requesting user as well as claimed player's info for notifications
            async with db.execute("""SELECT c.player_id, u.id, c.claimed_player_id, p.name
                                    FROM player_claims c
                                    LEFT JOIN users u ON u.player_id = c.player_id
                                    JOIN players p ON c.claimed_player_id = p.id
                                    WHERE c.id = ?""", (self.claim_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player claim not found", status=404)
                player_id, user_id, claimed_player_id, claimed_player_name = row

            # merge the claimed player's info into the new player
            await db.execute("UPDATE friend_codes SET player_id = ? WHERE player_id = ?", (player_id, claimed_player_id))
            await db.execute("UPDATE tournament_players SET player_id = ? WHERE player_id = ?", (player_id, claimed_player_id))
            await db.execute("UPDATE team_members SET player_id = ? WHERE player_id = ?", (player_id, claimed_player_id))
            await db.execute("UPDATE team_transfers SET player_id = ? WHERE player_id = ?", (player_id, claimed_player_id))
            # delete the player claim
            await db.execute("DELETE FROM player_claims WHERE id = ?", (self.claim_id,))
            # delete the claimed player after merging their data in
            await db.execute("DELETE FROM players WHERE id = ?", (claimed_player_id,))
            await db.commit()
            return player_id, user_id, claimed_player_name
               
@save_to_command_log
@dataclass
class DenyPlayerClaimCommand(Command[tuple[int, int, str]]):
    claim_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            # get the user id of requesting user as well as claimed player's info for notifications
            async with db.execute("""SELECT c.player_id, u.id, p.name
                                    FROM player_claims c
                                    LEFT JOIN users u ON u.player_id = c.player_id
                                    JOIN players p ON c.claimed_player_id = p.id
                                    WHERE c.id = ?""", (self.claim_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player claim not found", status=404)
                player_id, user_id, claimed_player_name = row
            await db.execute("UPDATE player_claims SET approval_status = ?", ("denied",))
            await db.commit()
            return player_id, user_id, claimed_player_name

@dataclass
class ListPlayerClaimsCommand(Command[list[PlayerClaim]]):
    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""SELECT c.id, c.date, c.approval_status,
                                  c.player_id, p1.name, p1.country_code, 
                                  c.claimed_player_id, p2.name, p2.country_code
                                  FROM player_claims c
                                  JOIN players p1 ON c.player_id = p1.id
                                  JOIN players p2 ON c.claimed_player_id = p2.id
                                  """) as cursor:
                claims: list[PlayerClaim] = []
                rows = await cursor.fetchall()
                for row in rows:
                    (claim_id, date, approval_status, player_id, player_name, player_country, 
                     claim_player_id, claim_player_name, claim_player_country) = row
                    player = PlayerBasic(player_id, player_name, player_country)
                    claimed_player = PlayerBasic(claim_player_id, claim_player_name, claim_player_country)
                    claims.append(PlayerClaim(claim_id, date, approval_status, player, claimed_player))
        return claims