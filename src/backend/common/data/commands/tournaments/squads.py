from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable
from common.auth import team_permissions
from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class CreateSquadCommand(Command[None]):
    squad_name: str | None
    squad_tag: str | None
    squad_color: int
    captain_player_id: int # captain of the squad
    tournament_id: int
    is_checked_in: bool
    is_bagger_clause: bool
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    is_approved: bool
    is_privileged: bool = False

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
            # check if tournament registrations are open and that our arguments are correct for the current tournament
            async with db.execute("SELECT is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_only, require_single_fc, bagger_clause_enabled, checkins_open FROM tournaments WHERE ID = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_only, require_single_fc, bagger_clause_enabled, checkins_open = row
                if not bool(is_squad):
                    raise Problem('This is not a squad tournament', status=400)
                if self.is_privileged is False and not bool(registrations_open):
                    raise Problem('Tournament registrations are closed', status=400)
                if bool(squad_tag_required) and self.squad_tag is None:
                    raise Problem('Tournament requires a tag for squads', status=400)
                if not bool(squad_tag_required) and self.squad_tag is not None:
                    raise Problem('Tournament does not accept squad tags, please set this value to null', status=400)
                if bool(squad_name_required) and self.squad_name is None:
                    raise Problem('Tournament requires a name for squads', status=400)
                if not bool(squad_name_required) and self.squad_name is not None:
                    raise Problem('Tournament does not accept squad names, please set this value to null', status=400)
                if bool(mii_name_required) and self.mii_name is None:
                    raise Problem('Tournament requires a Mii Name', status=400)
                if not bool(mii_name_required) and self.mii_name is not None:
                    raise Problem('Tournament does not accept Mii Names, please set this value to null', status=400)
                if bool(teams_only):
                    raise Problem('This tournament is teams only, cannot create new squads', status=400)
                if self.squad_tag and len(self.squad_tag) > 8:
                    raise Problem("Squad tags must be 8 characters or less", status=400)
                if self.squad_name and len(self.squad_name) > 32:
                    raise Problem("Squad names must be 32 characters or less", status=400)
                if self.squad_tag is not None and self.mii_name is not None:
                    if self.squad_tag not in self.mii_name:
                        raise Problem("Mii name must contain squad tag", status=400)
                if require_single_fc and not self.selected_fc_id:
                    raise Problem("Please select an FC to use for this tournament", status=400)
                if not bagger_clause_enabled and self.is_bagger_clause:
                    raise Problem("Cannot register as bagger when bagger clause is not enabled", status=400)

                selected_fc_id = self.selected_fc_id
                if not require_single_fc:
                    selected_fc_id = None
                    
            # check if player has already registered for the tournament
            async with db.execute("SELECT registration_id FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0 AND is_bagger_clause = ?", 
                                  (self.captain_player_id, self.tournament_id, self.is_bagger_clause)) as cursor:
                row = await cursor.fetchone()
                existing_registration_id = None
                if row:
                    existing_registration_id = row[0]
            if existing_registration_id is not None:
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_registrations WHERE id IS ?", (existing_registration_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    squad_is_registered = row[0]
                    if squad_is_registered == 1:
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            async with db.execute("""INSERT INTO tournament_registrations(name, tag, color, timestamp, tournament_id, is_registered, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (self.squad_name, self.squad_tag, self.squad_color, timestamp, self.tournament_id, True, self.is_approved)) as cursor:
                registration_id = cursor.lastrowid
            await db.commit()

            is_checked_in = True if bool(checkins_open) else self.is_checked_in
            
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                             is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.captain_player_id, self.tournament_id, registration_id, True, timestamp, is_checked_in, self.mii_name, self.can_host, False,
                selected_fc_id, False, self.is_bagger_clause, self.is_approved))
            await db.commit()

@save_to_command_log
@dataclass
class RegisterTeamTournamentCommand(Command[int | None]):
    tournament_id: int
    squad_name: str
    squad_tag: str
    squad_color: int
    creator_player_id: int
    roster_ids: list[int]
    players: list[TeamTournamentPlayer]
    is_approved: bool
    is_privileged: bool = False

    async def handle(self, db_wrapper, s3_wrapper) -> int | None:
        if len(self.roster_ids) == 0:
            raise Problem("Must register at least one roster", status=400)
        if not self.is_privileged and len(self.players) == 0:
            raise Problem("Must register at least one player", status=400)
        if len(set(self.roster_ids)) < len(self.roster_ids):
            raise Problem('Duplicate roster IDs detected', status=400)
        async with db_wrapper.connect() as db:
            # check if tournament registrations are open and that our arguments are correct for the current tournament
            async with db.execute("SELECT registrations_open, teams_allowed, min_representatives, min_squad_size, max_squad_size, bagger_clause_enabled, game, team_members_only FROM tournaments WHERE ID = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                registrations_open, teams_allowed, min_representatives, min_squad_size, max_squad_size, bagger_clause_enabled, game, team_members_only = row
                if not bool(teams_allowed):
                    raise Problem('This is not a team tournament', status=400)
                if self.is_privileged is False and not bool(registrations_open):
                    raise Problem('Tournament registrations are closed', status=400)
                captains = [p.player_id for p in self.players if p.is_captain]
                if len(self.players) and len(captains) != 1:
                    raise Problem(f"Exactly one player must be selected as a captain, but you have selected {len(captains)} captains", status=400)
                representatives = [p.player_id for p in self.players if p.is_captain or p.is_representative]
                if min_representatives and len(representatives) < min_representatives:
                    raise Problem(f'Must have at least {min_representatives} representatives for this tournament', status=400)
                baggers = [p.player_id for p in self.players if p.is_bagger_clause]
                if len(baggers) and not bool(bagger_clause_enabled):
                    raise Problem("Cannot register players as baggers when bagger clause is not enabled", status=400)
                if team_members_only and min_squad_size and len(self.players) < min_squad_size:
                    raise Problem(f"Number of players is less than this tournament's minimum squad size ({min_squad_size})", status=400)
                if max_squad_size and len(self.players) > max_squad_size:
                    raise Problem(f"Number of players is greater than this tournament's maximum squad size({max_squad_size})", status=400)
                
            # make sure creating player has permission for all rosters they are registering
            if len(self.roster_ids) > 0 and not self.is_privileged:
                async with db.execute(f"""
                    SELECT tr.id FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_rosters tr ON tr.team_id = ur.team_id
                    JOIN users u ON ur.user_id = u.id
                    JOIN players pl ON u.player_id = pl.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p ON rp.permission_id = p.id
                    WHERE pl.id = ? AND p.name = ? AND tr.id IN ({','.join([str(i) for i in self.roster_ids])})""",
                    (self.creator_player_id, team_permissions.REGISTER_TOURNAMENT)) as cursor:
                    # get all of the roster IDs in our list that the player has permissions for
                    rows = await cursor.fetchall()
                    roster_permissions = set([row[0] for row in rows])
                    # check if there are any missing rosters that we don't have permission for
                    if len(roster_permissions) < len(self.roster_ids):
                        missing_rosters = [i for i in self.roster_ids if i not in roster_permissions]
                        raise Problem(f"Missing permissions for following rosters: {missing_rosters}")
                    
            # check all rosters to make sure they are valid for this tournament
            for roster_id in self.roster_ids:
                async with db.execute("SELECT id, game FROM team_rosters WHERE id = ?", (roster_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise Problem(f"Roster with ID {roster_id} does not exist", status=400)
                    found_roster_id, found_roster_game = row
                    if found_roster_game != game:
                        raise Problem(f"Roster with ID {found_roster_id} is for the game {found_roster_game}, but this tournament is for {game}",
                                      status=400)

            # get players already registered for this tournament who are in rosters we are registering
            player_dict = {p.player_id: p for p in self.players}
            already_registered_query = f"""
                SELECT DISTINCT t.player_id, p.name, t.is_bagger_clause FROM tournament_players t
                JOIN team_members m ON m.player_id = t.player_id
                JOIN players p ON t.player_id = p.id
                WHERE m.roster_id IN ({','.join([str(i) for i in self.roster_ids])})
                AND t.tournament_id = ?
                """
            async with db.execute(already_registered_query, (self.tournament_id,)) as cursor:
                rows = await cursor.fetchall()
                already_registered_names: list[str] = []
                for row in rows:
                    player_id, name, is_bagger_clause = row
                    if player_id in player_dict:
                        player = player_dict[player_id]
                        if player.is_bagger_clause == bool(is_bagger_clause):
                            already_registered_names.append(name)
                if len(already_registered_names):
                    raise Problem(f"The following players are already registered for this tournament: {', '.join(already_registered_names)}",
                                  status=400)
                
            # make sure all the players in the request are part of the rosters we specified
            team_player_query = f"""
                SELECT m.player_id FROM team_members m
                JOIN players p ON m.player_id = p.id
                WHERE m.roster_id IN ({','.join([str(i) for i in self.roster_ids])})
                """
            async with db.execute(team_player_query) as cursor:
                rows = await cursor.fetchall()
                valid_players = set([row[0] for row in rows])
                invalid_players: list[int] = []
                for player in self.players:
                    if player.player_id not in valid_players:
                        invalid_players.append(player.player_id)
                if len(invalid_players):
                    player_ids = ', '.join([str(p) for p in invalid_players])
                    raise Problem(f"The following player IDs are not registered for any of the selected rosters: {', '.join(player_ids)}",
                                  status=400)
            
            timestamp = int(datetime.now(timezone.utc).timestamp())
            async with db.execute("""INSERT INTO tournament_registrations(name, tag, color, timestamp, tournament_id, is_registered, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (self.squad_name, self.squad_tag, self.squad_color, timestamp, self.tournament_id, True, self.is_approved)) as cursor:
                registration_id = cursor.lastrowid
            await db.commit()
            
            # link our rosters to this tournament squad
            team_squad_rows = [(roster, registration_id, self.tournament_id) for roster in self.roster_ids]
            await db.executemany("INSERT INTO team_squad_registrations(roster_id, registration_id, tournament_id) VALUES (?, ?, ?)", team_squad_rows)

            # add all our players to the squad
            queries_parameters: list[Iterable[Any]] = []
            for player in self.players:
                queries_parameters.append((player.player_id, self.tournament_id, registration_id, player.is_captain, timestamp, False, None, False, False, None, player.is_representative,
                                           player.is_bagger_clause, self.is_approved))
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                                    is_representative, is_bagger_clause, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", queries_parameters)
            await db.commit()
            return registration_id

@save_to_command_log
@dataclass
class EditSquadCommand(Command[None]):
    tournament_id: int
    registration_id: int
    squad_name: str | None
    squad_tag: str | None
    squad_color: int | None
    is_registered: bool | None
    is_approved: bool | None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_approved, name, tag, color, is_registered FROM tournament_registrations WHERE id = ? AND tournament_id = ?", (self.registration_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Squad not found", status=400)
                curr_is_approved, curr_name, curr_tag, curr_color, curr_registered = row
            is_approved = curr_is_approved if self.is_approved is None else self.is_approved
            name = curr_name if self.squad_name is None else self.squad_name
            tag = curr_tag if self.squad_tag is None else self.squad_tag
            color = curr_color if self.squad_color is None else self.squad_color
            is_registered = curr_registered if self.is_registered is None else self.is_registered
            async with db.execute("UPDATE tournament_registrations SET name = ?, tag = ?, color = ?, is_registered = ?, is_approved = ? WHERE id = ? AND tournament_id = ?",
                (name, tag, color, is_registered, is_approved, self.registration_id, self.tournament_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem("Squad not found", status=404)
            # unregister all players if squad is being withdrawn
            if not is_registered:
                await db.execute("DELETE FROM tournament_players WHERE registration_id = ? AND tournament_id = ?", (self.registration_id, self.tournament_id))
            await db.commit()

@dataclass
class CheckSquadCaptainPermissionsCommand(Command[None]):
    tournament_id: int
    registration_id: int
    captain_player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # check captain's permissions
            # whether they are actually in the squad and are captain,
            # or if they have register_tournament permissions for a roster
            # linked to that squad
            async with db.execute("""SELECT s.id FROM tournament_registrations s
                WHERE s.id = ? AND s.tournament_id = ? AND (
                    s.id IN (
                        SELECT p.registration_id FROM tournament_players p
                        WHERE p.player_id = ? AND p.is_squad_captain = 1
                    )
                    OR s.id IN (
                        SELECT tsr.registration_id FROM team_squad_registrations tsr
                        JOIN team_rosters r ON tsr.roster_id = r.id
                        JOIN teams t ON r.team_id = t.id
                        JOIN user_team_roles utr ON utr.team_id = t.id
                        JOIN users u ON utr.user_id = u.id
                        JOIN team_role_permissions trp ON trp.role_id = utr.role_id
                        JOIN team_permissions tp ON trp.permission_id = tp.id
                        WHERE tp.name = ? AND u.player_id = ?
                    )
                )""", (self.registration_id, self.tournament_id, self.captain_player_id, team_permissions.REGISTER_TOURNAMENT, self.captain_player_id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("You are not captain of this squad", status=400)
                
@dataclass
class ChangeSquadCaptainCommand(Command[None]):
    tournament_id: int
    registration_id: int
    new_captain_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND registration_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.registration_id, self.new_captain_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
            await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND registration_id = ?",
                             (False, self.tournament_id, self.registration_id))
            await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND registration_id = ? AND player_id = ?",
                             (True, self.tournament_id, self.registration_id, self.new_captain_id))
            await db.commit()

@dataclass
class AddRepresentativeCommand(Command[None]):
    tournament_id: int
    registration_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT max_representatives FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                max_representatives: int | None = row[0]
            async with db.execute("SELECT COUNT(*) FROM tournament_players WHERE tournament_id = ? AND registration_id = ? AND is_representative = 1",
                                  (self.tournament_id, self.registration_id)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                rep_count: int = row[0]
                if max_representatives and rep_count >= max_representatives:
                    raise Problem(f"This tournament has a maximum of {max_representatives} representatives", status=400)
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND registration_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.registration_id, self.player_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
                
            await db.execute("UPDATE tournament_players SET is_representative = 1 WHERE tournament_id = ? AND registration_id = ? AND player_id = ?",
                             (self.tournament_id, self.registration_id, self.player_id))
            await db.commit()

@dataclass
class RemoveRepresentativeCommand(Command[None]):
    tournament_id: int
    registration_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND registration_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.registration_id, self.player_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
                
            await db.execute("UPDATE tournament_players SET is_representative = 0 WHERE tournament_id = ? AND registration_id = ? AND player_id = ?",
                             (self.tournament_id, self.registration_id, self.player_id))
            await db.commit()

@dataclass
class UnregisterSquadCommand(Command[None]):
    tournament_id: int
    registration_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM tournament_players WHERE registration_id = ? AND tournament_id = ?", (self.registration_id, self.tournament_id))
            await db.execute("DELETE FROM team_squad_registrations WHERE registration_id = ? AND tournament_id = ?", (self.registration_id, self.tournament_id))
            await db.execute("DELETE FROM tournament_placements WHERE registration_id = ?", (self.registration_id,))
            await db.execute("DELETE FROM tournament_registrations WHERE id = ?", (self.registration_id,))
            await db.commit()

@dataclass
class GetSquadDetailsCommand(Command[TournamentSquadDetails]):
    tournament_id: int
    registration_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT id, name, tag, color, timestamp, is_registered, is_approved FROM tournament_registrations WHERE tournament_id = ? AND id = ?",
                (self.tournament_id, self.registration_id)) as cursor:
                squad_row = await cursor.fetchone()
                if not squad_row:
                    raise Problem("Squad not found", status=404)
                registration_id, name, tag, color, timestamp, is_registered, squad_is_approved = squad_row

            rosters: list[RosterBasic] = []
            # get teams connected to squads
            async with db.execute("""SELECT tsr.registration_id, tr.id, tr.team_id, tr.name, tr.tag, t.name, t.tag, t.color
                                  FROM team_squad_registrations tsr
                                  JOIN team_rosters tr ON tsr.roster_id = tr.id
                                  JOIN teams t ON tr.team_id = t.id
                                  WHERE tsr.registration_id = ?""", (self.registration_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    registration_id, roster_id, team_id, roster_name, roster_tag, team_name, team_tag, team_color = row
                    roster = RosterBasic(team_id, team_name, team_tag, team_color, roster_id, roster_name if roster_name else team_name, roster_tag if roster_tag else team_tag)
                    rosters.append(roster)

            async with db.execute("""SELECT t.id, t.player_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause, t.is_approved, t.is_eligible,
                                    p.name, p.country_code, p.is_banned, d.discord_id, d.username, d.discriminator, d.global_name, d.avatar
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    LEFT JOIN users u ON u.player_id = p.id
                                    LEFT JOIN user_discords d ON u.id = d.user_id
                                    WHERE t.registration_id IS ?""",
                                    (self.registration_id,)) as cursor:
                player_rows = await cursor.fetchall()
                players: list[SquadPlayerDetails] = []
                player_dict: dict[int, SquadPlayerDetails] = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list: list[int] = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve
                for row in player_rows:
                    (reg_id, player_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, 
                     can_host, is_invite, curr_fc_id, is_bagger_clause, player_is_approved, player_is_eligible, player_name, country, 
                     is_banned, discord_id, d_username, d_discriminator, d_global_name, d_avatar) = row
                    player_discord = None
                    if discord_id:
                        player_discord = Discord(discord_id, d_username, d_discriminator, d_global_name, d_avatar)
                    curr_player = SquadPlayerDetails(reg_id, player_id, self.registration_id, player_timestamp, is_checked_in, player_is_approved, player_is_eligible, mii_name, can_host,
                        player_name, country, bool(is_banned), player_discord, None, [], is_squad_captain, is_representative, is_invite, is_bagger_clause)
                    players.append(curr_player)

                    player_dict[curr_player.player_id] = curr_player
                    fc_id_list.append(curr_fc_id) # Add this FC's ID to the list of FCs we query for if require_single_fc is true for the current tournament
            # check if only single FCs are allowed or not
            async with db.execute("SELECT require_single_fc FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                require_single_fc = bool(row[0])
                fc_where_clause = ""
                if require_single_fc:
                    fc_where_clause = f" AND id IN ({','.join(map(str, fc_id_list))})" # convert all FC IDs to str and join with a comma
            # gathering all the valid FCs for each player for this tournament
            fc_query = f"SELECT player_id, fc FROM friend_codes WHERE player_id IN ({','.join(map(str, player_dict.keys()))}){fc_where_clause}"
            async with db.execute(fc_query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, fc = row
                    player_dict[player_id].friend_codes.append(fc)
            return TournamentSquadDetails(registration_id, name, tag, color, timestamp, is_registered, squad_is_approved, players, rosters)
        
@dataclass
class AddRosterToSquadCommand(Command[None]):
    tournament_id: int
    registration_id: int
    roster_id: int
    captain_player_id: int | None
    is_privileged: bool = False

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT game, mode, teams_allowed, registrations_open FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                game, mode, teams_allowed, registrations_open = row
            if not teams_allowed:
                raise Problem("Cannot add rosters to a squad if teams are not allowed", status=400)
            if not self.is_privileged and not registrations_open:
                raise Problem("This tournament's registrations are closed", status=400)
            async with db.execute("SELECT id FROM tournament_registrations WHERE id = ?", (self.registration_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Squad not found", status=404)
            async with db.execute("SELECT game, mode FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team roster not found", status=404)
                roster_game, roster_mode = row
                if game != roster_game or mode != roster_mode:
                    raise Problem("The tournament's game/mode and the roster's game/mode do not match", status=400)

            # make sure creating player has permission for all rosters they are registering
            if not self.is_privileged:
                async with db.execute("""
                    SELECT tr.id FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_rosters tr ON tr.team_id = ur.team_id
                    JOIN users u ON ur.user_id = u.id
                    JOIN players pl ON u.player_id = pl.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p ON rp.permission_id = p.id
                    WHERE pl.id = ? AND p.name = ? AND tr.id = ?""",
                    (self.captain_player_id, team_permissions.REGISTER_TOURNAMENT, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise Problem("You do not have permissions to register this roster for a tournament", status=400)
                
            async with db.execute("SELECT registration_id FROM team_squad_registrations WHERE tournament_id = ? AND roster_id = ?", (self.tournament_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem("This roster is already registered for this tournament", status=400)
                
            now = int(datetime.now(timezone.utc).timestamp())
            # get all players in the added roster who aren't already in the tournament
            async with db.execute("""SELECT m.player_id FROM team_members m
                                    WHERE m.roster_id = ? AND m.leave_date IS NULL
                                    AND m.player_id NOT IN (
                                        SELECT tp.player_id FROM tournament_players tp
                                        WHERE tournament_id = ? AND is_invite = ?
                                    )
                                  """, (self.roster_id, self.tournament_id, False)) as cursor:
                rows = await cursor.fetchall()
                new_players = [(row[0], self.tournament_id, self.registration_id, False, now, False, None, False, False, None, False, False, False) for row in rows]
            
            await db.execute("INSERT INTO team_squad_registrations(roster_id, registration_id, tournament_id) VALUES(?, ?, ?)", (self.roster_id, self.registration_id, self.tournament_id))
            await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, registration_id, is_squad_captain, timestamp, is_checked_in,
                                mii_name, can_host, is_invite, selected_fc_id, is_representative, is_approved, is_bagger_clause)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (new_players))
            await db.commit()

@dataclass
class RemoveRosterFromSquadCommand(Command[None]):
    tournament_id: int
    registration_id: int
    roster_id: int
    captain_player_id: int | None
    is_privileged: bool = False

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT registrations_open, teams_only FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                registrations_open, teams_only = row

            if not self.is_privileged and not registrations_open:
                raise Problem("This tournament's registrations are closed", status=400)
            
            async with db.execute("SELECT id FROM tournament_registrations WHERE id = ?", (self.registration_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Squad not found", status=404)
            async with db.execute("SELECT id FROM team_rosters WHERE id = ?", (self.roster_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Team roster not found", status=404)
            async with db.execute("SELECT registration_id FROM team_squad_registrations WHERE registration_id = ? AND roster_id = ?", (self.registration_id, self.roster_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("This roster is not linked with this squad", status=400)
                
            # prevent squad captain from unregistering themself accidentally
            if not self.is_privileged:
                async with db.execute("""SELECT id FROM tournament_players WHERE registration_id = ? AND player_id = ? AND tournament_id = ? AND player_id IN (
                                        SELECT player_id FROM team_members WHERE roster_id = ? AND leave_date IS NULL
                                      )""", (self.registration_id, self.captain_player_id, self.tournament_id, self.roster_id)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raise Problem("You cannot remove this roster from this squad as it would unregister yourself from the tournament.", status=400)
                
            await db.execute("DELETE FROM team_squad_registrations WHERE roster_id = ? AND registration_id = ? AND tournament_id = ?", (self.roster_id, self.registration_id, self.tournament_id))

            # if the tournament is teams only, players from the removed roster should be removed from the squad
            if teams_only:
                await db.execute("""DELETE FROM tournament_players WHERE registration_id = ? AND tournament_id = ? AND player_id IN (
                                        SELECT player_id FROM team_members WHERE roster_id = ? AND leave_date IS NULL
                                    )""", (self.registration_id, self.tournament_id, self.roster_id))
                
            await db.commit()