from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable
from common.auth import team_permissions
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, SquadPlayerDetails, TournamentSquadDetails


@save_to_command_log
@dataclass
class CreateSquadCommand(Command[None]):
    squad_name: str | None
    squad_tag: str | None
    squad_color: int
    creator_player_id: int # person who created the squad, may be different from the squad captain (ex. team tournaments where a team manager registers a squad they aren't in)
    captain_player_id: int # captain of the squad
    tournament_id: int
    is_checked_in: bool
    mii_name: str | None
    can_host: bool
    selected_fc_id: int | None
    roster_ids: list[int]
    representative_ids: list[int]
    bagger_ids: list[int]
    admin: bool = False

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        is_registered = True
        is_invite = False
        if len(set(self.roster_ids)) < len(self.roster_ids):
            raise Problem('Duplicate roster IDs detected', status=400)
        async with db_wrapper.connect() as db:
            # check if tournament registrations are open and that our arguments are correct for the current tournament
            async with db.execute("SELECT is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_allowed, teams_only, min_representatives, require_single_fc, bagger_clause_enabled FROM tournaments WHERE ID = ?",
                                  (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                is_squad, registrations_open, squad_tag_required, squad_name_required, mii_name_required, teams_allowed, teams_only, min_representatives, require_single_fc, bagger_clause_enabled = row
                if not bool(is_squad):
                    raise Problem('This is not a squad tournament', status=400)
                if self.admin is False and not bool(registrations_open):
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
                if not bool(teams_allowed) and len(self.roster_ids) > 0:
                    raise Problem('Teams are not allowed for this tournament', status=400)
                if bool(teams_only) and len(self.roster_ids) == 0:
                    raise Problem('Must specify at least one team roster ID for this tournament', status=400)
                # add 1 to the number of representative ids because the captain counts as a rep
                if min_representatives and len(self.representative_ids) + 1 < min_representatives:
                    raise Problem(f'Must have at least {min_representatives} representatives for this tournament', status=400)
                if self.squad_tag is not None and self.mii_name is not None:
                    if self.squad_tag not in self.mii_name:
                        raise Problem("Mii name must contain squad tag", status=400)
                if require_single_fc and not self.selected_fc_id:
                    raise Problem("Please select an FC to use for this tournament", status=400)
                if not bagger_clause_enabled and len(self.bagger_ids):
                    raise Problem("Cannot register players as baggers when bagger clause is not enabled", status=400)

                selected_fc_id = self.selected_fc_id
                if not require_single_fc:
                    selected_fc_id = None

            # make sure creating player has permission for all rosters they are registering
            if len(self.roster_ids) > 0 and not self.admin:
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
                    
            captain_is_bagger = self.captain_player_id in self.bagger_ids
            # check if player has already registered for the tournament
            async with db.execute("SELECT squad_id FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = 0 AND is_bagger_clause = ?", 
                                  (self.captain_player_id, self.tournament_id, captain_is_bagger)) as cursor:
                row = await cursor.fetchone()
                existing_squad_id = None
                if row:
                    existing_squad_id = row[0]
            if existing_squad_id is not None:
                # make sure player's squad isn't withdrawn before giving error
                async with db.execute("SELECT is_registered FROM tournament_squads WHERE id IS ?", (existing_squad_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    squad_is_registered = row[0]
                    if squad_is_registered == 1:
                        raise Problem('Player is already registered for this tournament', status=400)
                    
            async with db.execute("""INSERT INTO tournament_squads(name, tag, color, timestamp, tournament_id, is_registered)
                VALUES (?, ?, ?, ?, ?, ?)""", (self.squad_name, self.squad_tag, self.squad_color, timestamp, self.tournament_id, is_registered)) as cursor:
                squad_id = cursor.lastrowid
            await db.commit()
            
            if len(self.roster_ids) > 0:
                # create db link between squad and all rosters
                team_squad_rows = [(roster, squad_id, self.tournament_id) for roster in self.roster_ids]
                await db.executemany("INSERT INTO team_squad_registrations(roster_id, squad_id, tournament_id) VALUES (?, ?, ?)", team_squad_rows)
                # get players already registered for the tournament who are in the rosters we specified
                already_registered_query = f"""
                    SELECT t.player_id, t.is_bagger_clause FROM tournament_players t
                    JOIN team_members m ON m.player_id = t.player_id
                    WHERE m.roster_id IN ({','.join([str(i) for i in self.roster_ids])})
                    AND t.tournament_id = ?
                    """
                already_registered_players = []
                async with db.execute(already_registered_query, (self.tournament_id,)) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        player_id, is_bagger_clause = row
                        if is_bagger_clause and player_id in self.bagger_ids:
                            raise Problem(f"Player with ID {player_id} is already registered as a bagger for this tournament", status=400)
                        # if player isn't a bagger, add them to list of players we don't register
                        if not is_bagger_clause:
                            if player_id in self.representative_ids:
                                raise Problem(f"Player with ID {player_id} is already registered for this tournament, so they cannot be made a representative", status=400)
                            already_registered_players.append(player_id)

                # find all players not already registered for a different (registered) squad which we can register for the tournament
                players_query = f"""
                    SELECT m.player_id FROM team_members m
                    WHERE m.roster_id IN ({','.join([str(i) for i in self.roster_ids])})
                    """
                async with db.execute(players_query) as cursor:
                    rows = await cursor.fetchall()
                    valid_players = set([row[0] for row in rows if row[0] not in already_registered_players])
                    
                queries_parameters: list[Iterable[Any]] = []
                for p in valid_players:
                    if p == self.captain_player_id:
                        continue
                    is_representative = p in self.representative_ids
                    is_bagger = p in self.bagger_ids
                    queries_parameters.append((p, self.tournament_id, squad_id, False, timestamp, self.is_checked_in, None, False, False, None, is_representative, is_bagger))
                await db.executemany("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                                     is_representative, is_bagger_clause)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", queries_parameters)
            await db.execute("""INSERT INTO tournament_players(player_id, tournament_id, squad_id, is_squad_captain, timestamp, is_checked_in, mii_name, can_host, is_invite, selected_fc_id, 
                             is_representative, is_bagger_clause)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.captain_player_id, self.tournament_id, squad_id, True, timestamp, self.is_checked_in, self.mii_name, self.can_host, is_invite,
                selected_fc_id, False, captain_is_bagger))
            await db.commit()

@save_to_command_log
@dataclass
class EditSquadCommand(Command[None]):
    tournament_id: int
    squad_id: int
    squad_name: str
    squad_tag: str
    squad_color: int
    is_registered: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE tournament_squads SET name = ?, tag = ?, color = ?, is_registered = ? WHERE id = ? AND tournament_id = ?",
                (self.squad_name, self.squad_tag, self.squad_color, self.is_registered, self.squad_id, self.tournament_id)) as cursor:
                updated_rows = cursor.rowcount
                if updated_rows == 0:
                    raise Problem("Squad not found", status=404)
            # unregister all players if squad is being withdrawn
            if not self.is_registered:
                await db.execute("DELETE FROM tournament_players WHERE squad_id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id))
            await db.commit()

@dataclass
class CheckSquadCaptainPermissionsCommand(Command[None]):
    tournament_id: int
    squad_id: int
    captain_player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # check captain's permissions
            async with db.execute("SELECT squad_id, is_squad_captain FROM tournament_players WHERE player_id = ? AND tournament_id = ? AND is_invite = ?", 
                (self.captain_player_id, self.tournament_id, False)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("You are not registered for this tournament", status=400)
                captain_squad_id, is_squad_captain = row
                if captain_squad_id != self.squad_id:
                    raise Problem("You are not registered for this squad", status=400)
                if is_squad_captain == 0:
                    raise Problem("You are not captain of this squad", status=400)
                
@dataclass
class ChangeSquadCaptainCommand(Command[None]):
    tournament_id: int
    squad_id: int
    new_captain_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND squad_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.squad_id, self.new_captain_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
            await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND squad_id = ?",
                             (False, self.tournament_id, self.squad_id))
            await db.execute("UPDATE tournament_players SET is_squad_captain = ? WHERE tournament_id = ? AND squad_id = ? AND player_id = ?",
                             (True, self.tournament_id, self.squad_id, self.new_captain_id))
            await db.commit()

@dataclass
class AddRepresentativeCommand(Command[None]):
    tournament_id: int
    squad_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND squad_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.squad_id, self.player_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
                
            await db.execute("UPDATE tournament_players SET is_representative = 1 WHERE tournament_id = ? AND squad_id = ? AND player_id = ?",
                             (self.tournament_id, self.squad_id, self.player_id))
            await db.commit()

@dataclass
class RemoveRepresentativeCommand(Command[None]):
    tournament_id: int
    squad_id: int
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id FROM tournament_players WHERE tournament_id = ? AND squad_id = ? AND player_id = ? AND is_invite = ?",
                                  (self.tournament_id, self.squad_id, self.player_id, False)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Specified player is not in this squad", status=400)
                
            await db.execute("UPDATE tournament_players SET is_representative = 0 WHERE tournament_id = ? AND squad_id = ? AND player_id = ?",
                             (self.tournament_id, self.squad_id, self.player_id))
            await db.commit()

@dataclass
class UnregisterSquadCommand(Command[None]):
    tournament_id: int
    squad_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM tournament_players WHERE squad_id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id))
            await db.execute("DELETE FROM team_squad_registrations WHERE squad_id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id))
            await db.execute("UPDATE tournament_squads SET is_registered = 0 WHERE id = ? AND tournament_id = ?", (self.squad_id, self.tournament_id))
            await db.commit()

@dataclass
class GetSquadDetailsCommand(Command[TournamentSquadDetails]):
    tournament_id: int
    squad_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT id, name, tag, color, timestamp, is_registered FROM tournament_squads WHERE tournament_id = ? AND id = ?",
                (self.tournament_id, self.squad_id)) as cursor:
                squad_row = await cursor.fetchone()
                if not squad_row:
                    raise Problem("Squad not found", status=404)
                squad_id, name, tag, color, timestamp, is_registered = squad_row
            async with db.execute("""SELECT t.id, t.player_id, t.is_squad_captain, t.is_representative, t.timestamp, t.is_checked_in, 
                                    t.mii_name, t.can_host, t.is_invite, t.selected_fc_id, t.is_bagger_clause,
                                    p.name, p.country_code, p.discord_id
                                    FROM tournament_players t
                                    JOIN players p on t.player_id = p.id
                                    WHERE t.squad_id IS ?""",
                                    (self.squad_id,)) as cursor:
                player_rows = await cursor.fetchall()
                players: list[SquadPlayerDetails] = []
                player_dict: dict[int, SquadPlayerDetails] = {} # creating a dictionary of players so we can add their FCs to them later
                fc_id_list: list[int] = [] # if require_single_fc is true, we will need to know exactly which FCs to retrieve
                for row in player_rows:
                    reg_id, player_id, is_squad_captain, is_representative, player_timestamp, is_checked_in, mii_name, can_host, is_invite, curr_fc_id, is_bagger_clause, player_name, country, discord_id = row
                    curr_player = SquadPlayerDetails(reg_id, player_id, self.squad_id, player_timestamp, is_checked_in, mii_name, can_host,
                        player_name, country, discord_id, [], is_squad_captain, is_representative, is_invite, is_bagger_clause)
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
            return TournamentSquadDetails(squad_id, name, tag, color, timestamp, is_registered, players)