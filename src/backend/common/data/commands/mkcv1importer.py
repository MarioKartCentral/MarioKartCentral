
from dataclasses import dataclass

import bcrypt
import msgspec
from common.data import s3
from common.data.models.common import Problem, Game, GameMode
from common.data.models.mkcv1 import *
from common.data.models.users import UserLoginData
from common.data.models.tournaments import TournamentS3Fields
from common.data.commands import Command, save_to_command_log
from common.auth import roles, series_roles, team_roles
from datetime import datetime, timezone
import re

@dataclass
class ImportMKCV1DataCommand(Command[None]):
    data: MKCV1Data

    async def handle(self, db_wrapper, s3_wrapper):
        # These json files should not be public as they contain secrets, so store them with a private acl
        serialised_mkc: bytes = msgspec.json.encode(self.data.mkc)
        await s3_wrapper.put_object(s3.MKCV1_BUCKET, "mkc.json", serialised_mkc, acl="private")
        serialised_xf: bytes = msgspec.json.encode(self.data.xf)
        await s3_wrapper.put_object(s3.MKCV1_BUCKET, "xf.json", serialised_xf, acl="private")

@dataclass
class GetMKCV1DataCommand(Command[MKCData]):
    async def handle(self, db_wrapper, s3_wrapper):
        mkc_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "mkc.json")
        if mkc_bytes is None:
            raise Problem("MKCV1 data is not imported")
        return msgspec.json.decode(mkc_bytes, type=MKCData)

@dataclass
class GetXenforoUserDataCommand(Command[XFUser | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        xf_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "xf.json")
        if xf_bytes is None:
            raise Problem("MKC V1 data is not imported")
        xf_data = msgspec.json.decode(xf_bytes, type=XenforoData)

        for user in xf_data.xf_user:
            if user.user_id == self.id:
                return user

        return None

@dataclass
class ValidateXenforoPasswordCommand(Command[bool]):
    id: int
    password: str

    async def handle(self, db_wrapper, s3_wrapper):
        xf_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "xf.json")
        if xf_bytes is None:
            raise Problem("MKC V1 data is not imported")
        xf_data = msgspec.json.decode(xf_bytes, type=XenforoData)

        for user_auth in xf_data.xf_user_authenticate:
            if user_auth.user_id == self.id:
                bcrypt_hash = user_auth.data[22:82] # data is in format 'a:1:{s:4:"hash",s:60:"$2y$...";}'
                return bcrypt.checkpw(self.password.encode('utf-8'), bcrypt_hash.encode('utf-8'))
        
        return False

@dataclass
class GetMKCV1UserCommand(Command[NewMKCUser | None]):
    email: str
    password: str

    async def handle(self, db_wrapper, s3_wrapper):
        user_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "users.json")
        if user_bytes is None:
            return None # we shouldn't interrupt login flow if this fails
        user_data = msgspec.json.decode(user_bytes, type=NewMKCUserData)
        if self.email not in user_data.users:
            return None
        v1_user = user_data.users[self.email]
        # in the future, we may want to just accept and return the user even if the password is incorrect,
        # but require a password reset before you can use the site
        if not bcrypt.checkpw(self.password.encode('utf-8'), v1_user.password_hash.encode('utf-8')):
            raise Problem("Invalid login details", status=401)
        return v1_user

@save_to_command_log
@dataclass
class TransferMKCV1UserCommand(Command[UserLoginData]):
    email: str
    password_hash: str
    join_date: int
    player_id: int | None
    about_me: str | None
    user_roles: list[NewMKCUserRole]
    series_roles: list[NewMKCSeriesRole]
    team_roles: list[NewMKCTeamRole]

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            row = await db.execute_insert("INSERT INTO users(email, password_hash, join_date, player_id) VALUES (?, ?, ?, ?)", 
                                          (self.email, self.password_hash, self.join_date, self.player_id))
            # TODO: Run queries to identify why user creation failed
            if row is None:
                raise Problem("Failed to create user")
            user_id = int(row[0])

            is_banned = False
            expiration_date: int | None = None
            if self.player_id:
                async with db.execute("SELECT expiration_date FROM player_bans WHERE player_id = ?", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        is_banned = True
                        if row[0]:
                            expiration_date = int(row[0])

            # add about me from old site data
            await db.execute("INSERT INTO user_settings(user_id, about_me) VALUES(?, ?)", (user_id, self.about_me))

            # add user, series, team roles
            insert_user_roles: list[tuple[int, int, int | None]] = [(user_id, roles.id_by_default_role[role.role_name], None) for role in self.user_roles]
            if is_banned:
                insert_user_roles.append((user_id, roles.id_by_default_role[roles.BANNED], expiration_date))
            insert_series_roles = [(user_id, series_roles.id_by_default_role[role.role_name], role.series_id) for role in self.series_roles]
            insert_team_roles = [(user_id, team_roles.id_by_default_role[role.role_name], role.team_id) for role in self.team_roles]
            await db.executemany("""INSERT INTO user_roles(user_id, role_id, expires_on) VALUES(?, ?, ?)""", insert_user_roles)
            await db.executemany("""INSERT INTO user_series_roles(user_id, role_id, series_id) VALUES(?, ?, ?)""", insert_series_roles)
            await db.executemany("""INSERT INTO user_team_roles(user_id, role_id, team_id) VALUES(?, ?, ?)""", insert_team_roles)
            await db.commit()
            return UserLoginData(user_id, self.player_id, self.email, self.password_hash)

@save_to_command_log
@dataclass
class ConvertMKCV1DataCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper) -> None:
        # TODO (when added to data imports):
        # - Add placement upper bound
        # - Import series_templates when available

        # converts MKC's string timestamps to our int timestamps
        def get_mkc_timestamp(timestamp: str):
            return int(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp())

        xf_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "xf.json")
        if xf_bytes is None:
            raise Problem("MKC V1 data is not imported")
        xf_data = msgspec.json.decode(xf_bytes, type=XenforoData)

        # since passwords are stored separately, first create a dict mapping user id to
        # pw data
        xf_auth_dict: dict[int, XFUserAuthenticate] = {}
        for user_auth in xf_data.xf_user_authenticate:
            xf_auth_dict[user_auth.user_id] = user_auth

        # store these in a dict so we can add player IDs + roles later from the MKCV1 data
        xf_dict: dict[int, NewMKCUser] = {}
        for user in xf_data.xf_user:
            user_auth = xf_auth_dict.get(user.user_id, None)
            if user_auth:
                bcrypt_hash = user_auth.data[22:82] # data is in format 'a:1:{s:4:"hash",s:60:"$2y$...";}'
                new_user = NewMKCUser(user.user_id, user.username, user.email, user.register_date, bcrypt_hash, None, None, [], [], [])
                xf_dict[user.user_id] = new_user

        mkc_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "mkc.json")
        if mkc_bytes is None:
            raise Problem("MKCV1 data is not imported")
        mkc_data = msgspec.json.decode(mkc_bytes, type=MKCData)

        # initialize structures for things contained in the player data
        player_dict: dict[int, NewMKCPlayer] = {}
        friend_codes: list[NewMKCFriendCode] = []

        for player in mkc_data.players:
            user = None
            if player.user_id:
                user = xf_dict.get(player.user_id, None)
                if user:
                    user.player_id = player.id

            if len(player.profile_message) and user:
                user.about_me = player.profile_message

            join_date = get_mkc_timestamp(player.created_at)
            new_player = NewMKCPlayer(player.id, player.display_name, player.country, bool(player.is_hidden), player.user_id == None, False, join_date, user)
            player_dict[player.id] = new_player

            if player.switch_fc:
                friend_codes.append(NewMKCFriendCode(player.id, player.switch_fc, "switch"))
            if player.fc_3ds:
                friend_codes.append(NewMKCFriendCode(player.id, player.fc_3ds, "3ds"))
            if player.mktour_fc:
                friend_codes.append(NewMKCFriendCode(player.id, player.mktour_fc, "mkt"))
            if player.nnid:
                friend_codes.append(NewMKCFriendCode(player.id, player.nnid, "nnid"))
            
        now = int(datetime.now(timezone.utc).timestamp())
        player_bans: dict[int, NewMKCPlayerBan] = {}
        historical_bans: list[NewMKCHistoricalBan] = []
        
        for ban in mkc_data.player_bans:
            if ban.end_date is None:
                player = player_dict.get(ban.player_id, None)
                if player:
                    player.is_banned = True
            ban_date = get_mkc_timestamp(ban.start_date)
            unban_date =  get_mkc_timestamp(ban.end_date) if ban.end_date else 0
            banned_by_player = player_dict[ban.banned_by]
            if ban.end_date is None or unban_date > now:
                new_ban = NewMKCPlayerBan(ban.player_id, 0, ban.end_date is None, ban_date, unban_date, ban.reason, f"Banned by: {banned_by_player.name} ({banned_by_player.id})")
                player_bans[ban.player_id] = new_ban
            else:
                historical_bans.append(NewMKCHistoricalBan(ban.player_id, 0, None, unban_date, False, ban_date, unban_date, ban.reason, f"Banned by: {banned_by_player.name} ({banned_by_player.id})"))

        user_role_map = {
            "administrate": roles.ADMINISTRATOR,
            "event_admin": roles.EVENT_ADMIN,
            "event_mod": roles.EVENT_MOD,
            "moderate": roles.SITE_MODERATOR,
            "supporter": roles.SITE_SUPPORTER,
        }
        for player_role in mkc_data.player_roles:
            player = player_dict.get(player_role.player_id, None)
            if not player or not player.user:
                continue
            if player_role.role.startswith("series_admin:"):
                series_id = int(player_role.role.replace("series_admin:", ""))
                player.user.series_roles.append(NewMKCSeriesRole(series_roles.ADMINISTRATOR, series_id))
                continue
            if player_role.role.startswith("series_mod:"):
                series_id = int(player_role.role.replace("series_mod:", ""))
                player.user.series_roles.append(NewMKCSeriesRole(series_roles.ORGANIZER, series_id))
                continue
            new_role_name = user_role_map[player_role.role]
            player.user.user_roles.append(NewMKCUserRole(new_role_name))

        # map language strings on old site to language strings on new site.
        # for some reason the old site let you put in a custom language,
        # so we'll just change all the extraneous ones to english
        language_map: dict[str, str] = {
            'German': 'de',
            'English': 'en-us',
            'French': 'fr',
            'Spanish': 'es',
            'Japanese': 'ja'
        }
        # map team approval on old site to approval status on new site
        team_approval_map: dict[str, str] = {
            "approved": "approved",
            "banned": "denied",
            "unapproved": "pending",
            "disapproved": "denied"
        }

        # map old site game-modes to new site game/mode
        game_mode_map: dict[str, tuple[Game, GameMode]] = {
            "150cc": ("mk8dx", "150cc"),
            "200cc": ("mk8dx", "200cc"),
            "mk7_vs": ("mk7", "vsrace"),
            "mk8u_150cc": ("mk8", "150cc"),
            "mk8u_200cc": ("mk8", "200cc"),
            "mktour_vs": ("mkt", "vsrace"),
            "mkw_vs": ("mkw", "rt")
        }
        team_dict: dict[int, NewMKCTeam] = {}
        roster_dict: dict[int, NewMKCTeamRoster] = {}
        # we will use this to have incrementing IDs before we put them in the database
        roster_id = 1
        for team in mkc_data.teams:
            new_language = language_map.get(team.main_language, 'en-us')
            new_approval = team_approval_map[team.status]
            creation_date = get_mkc_timestamp(team.created_at)
            recruitment_status = team.recruitment_status == "recruiting"
            logo = None # change to team.picture_filename later
            new_team = NewMKCTeam(team.id, team.team_name, team.team_tag, team.team_description, creation_date, new_language, team.color_number,
                                  logo, new_approval, bool(team.is_historical or team.is_shadow), recruitment_status, {})
            team_dict[team.id] = new_team

            # create a team roster if the category is one that doesn't have rosters on the old site
            # (old site only has rosters for mk8dx 150cc, mk8dx 200cc, mktour vs race)
            if team.team_category in ["mk7_vs", "mk8u_150cc", "mk8u_200cc", "mkw_vs"]:
                game, mode = game_mode_map[team.team_category]
                roster = NewMKCTeamRoster(roster_id, team.id, game, mode, None, None, creation_date, team.recruitment_status == "recruiting", False, new_approval, [])
                roster_id += 1
                new_team.rosters[team.team_category] = roster
                roster_dict[roster.id] = roster

            if team.manager_player_id:
                player = player_dict[team.manager_player_id]
                if player.user:
                    player.user.team_roles.append(NewMKCTeamRole(team_roles.MANAGER, team.id))

        for roster in mkc_data.team_rosters:
            team = team_dict[roster.team_id]
            game, mode = game_mode_map[roster.roster_category]
            new_roster = NewMKCTeamRoster(roster_id, team.id, game, mode, None, None, team.creation_date, team.is_recruiting, bool(roster.roster_active), team.approval_status, [])
            roster_id += 1
            team.rosters[roster.roster_category] = new_roster
            roster_dict[new_roster.id] = new_roster

        team_members: list[NewMKCTeamMember] = []
        for team_member in mkc_data.team_memberships:
            team = team_dict[team_member.team_id]
            # There are about 55 cases where this condition occurs, all of them are from staff accidentally
            # registering a player for the team's wrong mode (ex. registering a player for 150cc when it's a 200cc team)
            if team_member.roster_category not in team.rosters:
                continue
            roster = team.rosters[team_member.roster_category]
            join_date = get_mkc_timestamp(team_member.joined)
            leave_date = get_mkc_timestamp(team_member.left) if team_member.left else None
            # give user leader role if they are in the team and are team leader
            if not leave_date and team_member.team_leader:
                player = player_dict[team_member.player_id]
                if player.user:
                    player.user.team_roles.append(NewMKCTeamRole(team_roles.LEADER, team.id))
            new_member = NewMKCTeamMember(roster.id, team_member.player_id, join_date, leave_date)
            roster.members.append(new_member)
            team_members.append(new_member)
        
        transfers: list[NewMKCTransfer] = []
        transfer_approval_map = {
            "accepted" : "approved",
            "rejected_by_mod": "denied",
            "invited": "pending"
        }
        for transfer in mkc_data.transfers:
            from_roster_id = None
            if transfer.from_team:
                old_team = team_dict[transfer.from_team]
                if transfer.roster_category not in old_team.rosters:
                    continue
                from_roster_id = old_team.rosters[transfer.roster_category].id
            to_roster_id = None
            if transfer.to_team:
                new_team = team_dict[transfer.to_team]
                if transfer.roster_category not in new_team.rosters:
                    continue
                to_roster_id = new_team.rosters[transfer.roster_category].id
            date = get_mkc_timestamp(transfer.created_at)
            # on the new site we just delete transfers that are canceled/declined, so we don't need to move these over.
            # for some reason there are a bunch of random transfers labeled "invited" from years ago
            # that are invisible on the current site, and it's impossible to invite people to teams
            # on the old site currently anyway, so we also delete transfers which are labeled as "invited".
            if transfer.status in ["cancelled_by_team", "decline", "declined", "invited"]:
                continue
            
            is_accepted = transfer.status in ["accepted", "rejected_by_mod"]
            approval_status = transfer_approval_map[transfer.status]
            new_transfer = NewMKCTransfer(transfer.player_id, to_roster_id, from_roster_id, date, is_accepted, approval_status)
            transfers.append(new_transfer)

        organizer_map = {
            "mkc": "MKCentral",
            "affiliate": "Affiliate",
            "lan": "LAN",
        }
        tournament_mode_map: dict[MKCGameMode, tuple[Game, GameMode]] = {
            "mk8dx_150": ("mk8dx", "150cc"),
            "mk8dx_200": ("mk8dx", "200cc"),
            "mk8dx_battle_bobomb": ("mk8dx", "bobomb_blast"),
            "mk8dx_battle_coin": ("mk8dx", "coin_runners"),
            "mk8dx_battle_renegade": ("mk8dx", "renegade_roundup"),
            "mk8dx_battle_shine": ("mk8dx", "shine_thief"),
            "mk8dx_mixed": ("mk8dx", "mixed"),
            "mk8u_150": ("mk8", "150cc"),
            "mk8u_200": ("mk8", "200cc"),
            "mk7_vs_race": ("mk7", "vsrace"),
            "mktour_vs_race": ("mkt", "vsrace"),
            "mkw_vs_race": ("mkw", "rt"),
            "smk_match_race": ("smk", "match_race"),
            "switch_other": ("mk8dx", "150cc"), # technically not accurate but this is just used for 2 pokemon tournaments lol
        }
        series_dict: dict[int, NewMKCSeries] = {}
        for series in mkc_data.tournament_series:
            game, mode = tournament_mode_map[series.default_game_mode] if series.default_game_mode else ("mk8dx", "150cc")
            organizer = organizer_map[series.organizer]
            logo = None # change to series.logo_filename later
            new_series = NewMKCSeries(series.id, series.series_name, series.url_slug, series.display_order, game, mode, bool(series.historical), bool(series.published),
                                      series.short_description, series.full_description if series.full_description else "", "", logo, organizer, series.location)
            series_dict[series.id] = new_series

        
        tournament_dict: dict[int, NewMKCTournament] = {}
        for tournament in mkc_data.events:
            game, mode = tournament_mode_map[tournament.game_mode]
            organizer = organizer_map[tournament.organizer]
            # all tournaments without start/end dates are marked as 'delete'
            # so don't need to worry about them
            if not tournament.start_date or not tournament.end_date:
                continue
            # check if tournament is squad/team tournament
            is_squad = tournament.event_format in ['0', '2']
            # all team tournaments from old site should have these properties to be true
            teams_allowed = tournament.event_format == '0'
            teams_only = tournament.event_format == '0'
            team_members_only = tournament.event_format == '0'
            # need these both to be true to show team names/tags in team tournaments
            squad_tag_required = True if teams_allowed else bool(tournament.team_tag_required)
            squad_name_required = True if teams_allowed else bool(tournament.team_name_required)

            date_start = get_mkc_timestamp(tournament.start_date)
            date_end = get_mkc_timestamp(tournament.end_date)
            registration_deadline = get_mkc_timestamp(tournament.transfer_date) if tournament.transfer_date else None
            logo = None # change to tournament.logo_filename later
            new_tournament = NewMKCTournament(tournament.id, tournament.title, game, mode,
                                              tournament.tournament_series_id, is_squad,
                                              bool(tournament.registrations_open), date_start, 
                                              date_end, tournament.description, False, bool(tournament.series_stats_include),
                                              logo, False, None, registration_deadline, None,
                                              teams_allowed, teams_only, team_members_only, tournament.minimum_team_size,
                                              tournament.maximum_team_size, squad_tag_required,
                                              squad_name_required, bool(tournament.player_mii_name_required),
                                              bool(tournament.player_host_required), bool(tournament.checkin_required),
                                              tournament.checkin_status == 1, tournament.checkin_minimum, bool(tournament.verification_required),
                                              False, bool(tournament.published), bool(tournament.published), False, bool(tournament.show_on_profiles),
                                              False, None, False, False, organizer, tournament.location, tournament.rules
                                              )
            tournament_dict[tournament.id] = new_tournament

        # we'll be going back and forth between these structs a lot so just make them into dictionaries for O(1) access
        squad_dict: dict[int, MKCSquad] = {s.id: s for s in mkc_data.squads}
        placement_dict: dict[int, MKCEventPlacement] = {p.event_registration_id: p for p in mkc_data.event_placements}
        # set of tuples of type (event registration id, player id) so we can easily check if a player is opted out
        # of a tournament, and not add them to the tournament
        optouts = {(o.event_registration_id, o.player_id) for o in mkc_data.player_optouts}
        # set of tuples of type (event registration id, player id) to add players as representatives for team tournaments
        team_representatives = {(r.event_registration_id, r.player_id) for r in mkc_data.team_representatives}

        tournament_player_id = 1 # once again we need to increment IDs on our own since this is a new table
        tournament_squad_id = max([squad.id for squad in mkc_data.squads]) + 1 # we will need to make some new squads for team registrations,
                                                                                    # so we use this to increment IDs
        new_squads: list[NewMKCSquad] = []
        new_tournament_players: list[NewMKCTournamentPlayer] = []
        tournament_player_dict: dict[int, NewMKCTournamentPlayer] = {} # map event registration IDs to our new tournament player IDs for placements
        new_squad_dict: dict[int, NewMKCSquad] = {}
        roster_squad_links: list[NewMKCRosterSquadLink] = []
        solo_placements: list[NewMKCSoloPlacement] = []
        squad_placements: list[NewMKCSquadPlacement] = []
        tournament_team_map: dict[tuple[Game, GameMode], TeamMode] = { # map game/mode from our new tournaments to old game/mode used for identifying team rosters
            ("mk8dx", "150cc"): "150cc",
            ("mk8dx", "200cc"): "200cc",
            ("mk7", "vsrace"): "mk7_vs",
            ("mkw", "rt"): "mkw_vs",
            ("mkt", "vsrace"): "mktour_vs",
            ("mk8", "150cc"): "mk8u_150cc",
            ("mk8", "200cc"): "mk8u_200cc",
        }
        squad_regex = re.compile(r"Squad [0-9]+")
        for reg in mkc_data.event_registrations:
            timestamp = get_mkc_timestamp(reg.created_at)
            if reg.event_id not in tournament_dict:
                continue
            tournament = tournament_dict[reg.event_id]
            # if the registation has a squad ID linked, we just recreate that squad, adding members later on from the squad_memberships table
            if reg.squad_id:
                squad = squad_dict[reg.squad_id]
                # Old site stores squad name as "Squad #" if it has no name, we would like to just set it to None instead
                squad_name = squad.squad_name if not re.match(squad_regex, squad.squad_name) else None
                new_squad = NewMKCSquad(squad.id, squad_name, squad.squad_tag, squad.color_number, timestamp, reg.event_id, reg.status == "registered",
                                        bool(reg.verified))
                new_squads.append(new_squad)
                new_squad_dict[new_squad.id] = new_squad
                if reg.id in placement_dict:
                    placement = placement_dict[reg.id]
                    new_placement = NewMKCSquadPlacement(tournament.id, new_squad.id, placement.placement, placement.title, None, bool(placement.disqualified))
                    squad_placements.append(new_placement)
            # in the case that the registration has a team linked, we need to make a new squad with all of the members of the team that were in it at the time.
            elif reg.team_id:
                team = team_dict[reg.team_id]
                

                roster_mode = tournament_team_map[(tournament.game, tournament.mode)]
                if roster_mode not in team.rosters:
                    new_roster = NewMKCTeamRoster(roster_id, team.id, tournament.game, tournament.mode, None, None, team.creation_date, team.is_recruiting, False, team.approval_status, [])
                    team.rosters[roster_mode] = new_roster
                    roster_dict[roster_id] = new_roster
                    roster_id += 1
                roster = team.rosters[roster_mode]
                squad_name = roster.name if roster.name else team.name
                squad_tag = roster.tag if roster.tag else team.tag
                
                new_squad = NewMKCSquad(tournament_squad_id, squad_name, squad_tag, team.color, timestamp, tournament.id, reg.status == "registered",
                                        bool(reg.verified))
                new_squads.append(new_squad)
                new_squad_dict[new_squad.id] = new_squad
                tournament_squad_id += 1
                # link up our team roster with the created squad
                roster_squad_link = NewMKCRosterSquadLink(roster.id, new_squad.id, tournament.id)
                roster_squad_links.append(roster_squad_link)
                for member in roster.members:
                    # we want to only add roster members that were registered for the tournament the whole way through
                    if tournament.registration_deadline and member.join_date > tournament.registration_deadline:
                        continue
                    if member.leave_date and member.leave_date < tournament.date_end:
                        continue
                    # on the new site players can just unregister themselves from the tournament instead of opting out.
                    # therefore just skip over any members that are opted out
                    if (reg.id, member.player_id) in optouts:
                        continue
                    # set a player as representative for their squad if they are one for the event registration
                    is_representative = (reg.id, member.player_id) in team_representatives
                    new_player = NewMKCTournamentPlayer(tournament_player_id, member.player_id, tournament.id, new_squad.id, False,
                                                        timestamp, False, None, False, False, None, is_representative, bool(reg.verified))
                    new_tournament_players.append(new_player)
                    tournament_player_id += 1
                if reg.id in placement_dict:
                    placement = placement_dict[reg.id]
                    new_placement = NewMKCSquadPlacement(tournament.id, new_squad.id, placement.placement, placement.title, None, bool(placement.disqualified))
                    squad_placements.append(new_placement)
            # if the registration is for a single player (solo tournaments)
            else:
                new_player = NewMKCTournamentPlayer(tournament_player_id, reg.player_id, reg.event_id, None, False, timestamp,
                                                    bool(reg.checked_in), reg.mii_name, bool(reg.player_can_host), False, None,
                                                    False, bool(reg.verified))
                new_tournament_players.append(new_player)
                tournament_player_dict[reg.id] = new_player # add to the tournament_player_dict for placements later
                tournament_player_id += 1
                if reg.id in placement_dict:
                    placement = placement_dict[reg.id]
                    new_placement = NewMKCSoloPlacement(tournament.id, new_player.id, placement.placement, placement.title, None, bool(placement.disqualified))
                    solo_placements.append(new_placement)

        for player in mkc_data.squad_memberships:
            # there are 16 cases where this is true for some reason,
            # they are all from years ago so maybe just a mistake.
            # just skip over these cases
            if player.squad_id not in new_squad_dict:
                continue
            # we just delete these on new site if player rejects/unregisters
            if player.status in ["cancelled", "declined", "withdrawn", "kicked"]:
                continue
            squad = new_squad_dict[player.squad_id]
            timestamp = get_mkc_timestamp(player.created_at)
            new_player = NewMKCTournamentPlayer(tournament_player_id, player.player_id, squad.tournament_id, squad.id, bool(player.captain),
                                                timestamp, bool(player.checked_in), player.mii_name, bool(player.player_can_host),
                                                player.status == "invited", None, False, False)
            new_tournament_players.append(new_player)
            tournament_player_id += 1
        
        async with db_wrapper.connect() as db:
            # inserting/modifying players
            inserts = [(player.id, player.name, player.country_code, player.is_hidden, player.is_shadow, player.is_banned, player.join_date)
                    for player in player_dict.values()]
            await db.executemany("""INSERT INTO players(id, name, country_code, is_hidden, is_shadow, is_banned, join_date)
                                            VALUES(?, ?, ?, ?, ?, ?, ?)""", inserts)

            # friend codes
            await db.executemany("""INSERT INTO friend_codes(player_id, type, fc, is_verified, is_primary, is_active, description)
                                    VALUES(?, ?, ?, ?, ?, ?, ?)""",
                                    [(fc.player_id, fc.type, fc.fc, False, True, True, None) for fc in friend_codes])
            
            # bans
            await db.executemany("""INSERT INTO player_bans(player_id, banned_by, is_indefinite, ban_date, expiration_date, reason, comment)
                                    VALUES(?, ?, ?, ?, ?, ?, ?)""",
                                    [(ban.player_id, ban.banned_by, ban.is_indefinite, ban.ban_date, ban.expiration_date, ban.reason, ban.comment) for ban in player_bans.values()])
            await db.executemany("""INSERT INTO player_bans_historical(player_id, banned_by, unbanned_by, unban_date, is_indefinite, ban_date, 
                                    expiration_date, reason, comment) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(ban.player_id, ban.banned_by, ban.unbanned_by, ban.unban_date, ban.is_indefinite, ban.ban_date,
                                      ban.expiration_date, ban.reason, ban.comment) for ban in historical_bans])
            
            # teams
            await db.executemany("""INSERT INTO teams(id, name, tag, description, creation_date, language, color, logo, approval_status, is_historical)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(team.id, team.name, team.tag, team.description, team.creation_date, team.language, team.color, team.logo,
                                      team.approval_status, team.is_historical) for team in team_dict.values()])
            await db.executemany("""INSERT INTO team_rosters(id, team_id, game, mode, name, tag, creation_date, is_recruiting, is_active, approval_status)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(r.id, r.team_id, r.game, r.mode, r.name, r.tag, r.creation_date, r.is_recruiting, r.is_active, r.approval_status)
                                      for r in roster_dict.values()])
            await db.executemany("""INSERT INTO team_members(roster_id, player_id, join_date, leave_date, is_bagger_clause)
                                    VALUES(?, ?, ?, ?, ?)""",
                                    [(m.roster_id, m.player_id, m.join_date, m.leave_date, False) for m in team_members])
            await db.executemany("""INSERT INTO team_transfers(player_id, roster_id, date, roster_leave_id, is_bagger_clause, is_accepted, approval_status)
                                    VALUES(?, ?, ?, ?, ?, ?, ?)""",
                                    [(t.player_id, t.roster_id, t.date, t.roster_leave_id, False, t.is_accepted, t.approval_status) for t in transfers])

            # tournaments
            await db.executemany("""INSERT INTO tournament_series(id, name, url, display_order, game, mode, is_historical, is_public, short_description, logo,
                                    organizer, location)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(s.id, s.series_name, s.url, s.display_order, s.game, s.mode, s.is_historical, s.is_public, s.short_description, s.logo,
                                      s.organizer, s.location)
                                      for s in series_dict.values()])
            for series in series_dict.values():
                s3_message = bytes(msgspec.json.encode(series))
                await s3_wrapper.put_object(s3.SERIES_BUCKET, f'{series.id}.json', s3_message)
            
            await db.executemany("""INSERT INTO tournaments(id, name, game, mode, series_id, is_squad, registrations_open, date_start, date_end,
                                    use_series_description, series_stats_include, logo, use_series_logo, url, registration_deadline,
                                    registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                                    squad_name_required, mii_name_required, host_status_required, checkins_enabled, checkins_open, min_players_checkin,
                                    verification_required, verified_fc_required, is_viewable, is_public, is_deleted, show_on_profiles, require_single_fc,
                                    min_representatives, bagger_clause_enabled, use_series_ruleset, organizer, location)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(t.id, t.name, t.game, t.mode, t.series_id, t.is_squad, t.registrations_open, t.date_start, t.date_end,
                                      t.use_series_description, t.series_stats_include, t.logo, t.use_series_logo, t.url,
                                      t.registration_deadline, t.registration_cap, t.teams_allowed, t.teams_only, t.team_members_only, t.min_squad_size,
                                      t.max_squad_size, t.squad_tag_required, t.squad_name_required, t.mii_name_required, t.host_status_required,
                                      t.checkins_enabled, t.checkins_open, t.min_players_checkin, t.verification_required, t.verified_fc_required,
                                      t.is_viewable, t.is_public, t.is_deleted, t.show_on_profiles, t.require_single_fc, t.min_representatives,
                                      t.bagger_clause_enabled, t.use_series_ruleset, t.organizer, t.location) for t in tournament_dict.values()])
            for tournament in tournament_dict.values():
                s3_body = TournamentS3Fields(tournament.description, tournament.ruleset)
                s3_message = bytes(msgspec.json.encode(s3_body))
                await s3_wrapper.put_object(s3.TOURNAMENTS_BUCKET, f'{tournament.id}.json', s3_message)

            # tournament registrations
            await db.executemany("""INSERT INTO tournament_squads(id, name, tag, color, timestamp, tournament_id, is_registered, is_approved)
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(s.id, s.name, s.tag, s.color, s.timestamp, s.tournament_id, s.is_registered, s.is_approved) for s in new_squads])
            await db.executemany("""INSERT INTO tournament_players(id, player_id, tournament_id, squad_id, is_squad_captain, timestamp,
                                    is_checked_in, mii_name, can_host, is_invite, selected_fc_id, is_representative, is_bagger_clause,
                                    is_approved) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    [(p.id, p.player_id, p.tournament_id, p.squad_id, p.is_squad_captain, p.timestamp,
                                      p.is_checked_in, p.mii_name, p.can_host, p.is_invite, p.selected_fc_id, p.is_representative,
                                      False, p.is_approved) for p in new_tournament_players])
            await db.executemany("""INSERT INTO team_squad_registrations(roster_id, squad_id, tournament_id)
                                    VALUES(?, ?, ?)""", [(r.roster_id, r.squad_id, r.tournament_id) for r in roster_squad_links])
            
            # tournament placements
            await db.executemany("""INSERT INTO tournament_solo_placements(tournament_id, player_id, placement, placement_description, placement_lower_bound, is_disqualified)
                                    VALUES(?, ?, ?, ?, ?, ?)""", [(p.tournament_id, p.player_id, p.placement, p.placement_description, p.placement_lower_bound,
                                                                   p.is_disqualified) for p in solo_placements])
            await db.executemany("""INSERT INTO tournament_squad_placements(tournament_id, squad_id, placement, placement_description, placement_lower_bound, is_disqualified)
                                 VALUES(?, ?, ?, ?, ?, ?)""", [(p.tournament_id, p.squad_id, p.placement, p.placement_description, p.placement_lower_bound,
                                                                   p.is_disqualified) for p in squad_placements])
            await db.commit()

        # create a new S3 file which lets us retrieve a user's info easier upon first login
        new_users = {u.email: u for u in xf_dict.values()}
        user_data = NewMKCUserData(new_users)
        s3_message = bytes(msgspec.json.encode(user_data))
        await s3_wrapper.put_object(s3.MKCV1_BUCKET, f'users.json', s3_message)