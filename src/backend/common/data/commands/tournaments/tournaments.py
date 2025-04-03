from dataclasses import dataclass

import msgspec

from common.data.commands import Command, save_to_command_log
from common.data.models import *
from common.auth import tournament_permissions
import common.data.s3 as s3
from aiosqlite import Row
import base64

@save_to_command_log
@dataclass
class CreateTournamentCommand(Command[int | None]):
    body: CreateTournamentRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        # check for invalid body parameters
        if not b.is_squad and b.teams_allowed:
            raise Problem('Individual tournaments cannot have teams linked', status=400)
        if not b.teams_allowed and (b.teams_only or b.team_members_only):
            raise Problem('Non-team tournaments cannot have teams_only, team_members_only, min_representatives enabled', status=400)
        if not b.is_squad and (b.min_squad_size or b.max_squad_size or b.squad_tag_required or b.squad_name_required):
            raise Problem('Individual tournaments may not have settings for min_squad_size, max_squad_size, squad_tag_required, squad_name_required', status=400)
        if b.teams_allowed and (b.mii_name_required or b.host_status_required or b.require_single_fc):
            raise Problem('Team tournaments cannot have mii_name_required, host_status_required, or require_single_fc enabled', status=400)
        if b.teams_allowed and (not b.squad_tag_required or not b.squad_name_required):
            raise Problem('Team tournaments must require a squad tag/name', status=400)
        if not b.series_id and b.use_series_logo:
            raise Problem('Cannot use series logo if no series is selected', status=400)
        if b.bagger_clause_enabled and not (b.game == 'mkw' and b.is_squad):
            raise Problem('Game must be set to MKW and it must be a squad tournament to use bagger clause', status=400)

        # store minimal data about each tournament in the SQLite DB
        async with db_wrapper.connect() as db:
            cursor = await db.execute(
                """INSERT INTO tournaments(
                    name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, use_series_description, series_stats_include,
                    logo, use_series_logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                    squad_name_required, mii_name_required, host_status_required, checkins_enabled, checkins_open, min_players_checkin, verification_required, verified_fc_required, is_viewable,
                    is_public, is_deleted, show_on_profiles, require_single_fc, min_representatives, bagger_clause_enabled, use_series_ruleset, organizer, location
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.name, b.game, b.mode, b.series_id, b.is_squad, b.registrations_open, b.date_start, b.date_end, b.use_series_description,
                b.series_stats_include, None, b.use_series_logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_enabled, b.checkins_open, b.min_players_checkin, 
                b.verification_required, b.verified_fc_required, b.is_viewable, b.is_public, b.is_deleted, b.show_on_profiles, b.require_single_fc, b.min_representatives,
                b.bagger_clause_enabled, b.use_series_ruleset, b.organizer, b.location))
            tournament_id = cursor.lastrowid

            logo_filename = f"tournament_logos/{tournament_id}.png"
            logo_path = f"/img/{logo_filename}"
            if b.logo_file:
                await db.execute("UPDATE tournaments SET logo = ? WHERE id = ?", (logo_path, tournament_id))
            

            s3_body = TournamentS3Fields(b.description, b.ruleset)
            s3_message = bytes(msgspec.json.encode(s3_body))
            await s3_wrapper.put_object(s3.TOURNAMENTS_BUCKET, f'{tournament_id}.json', s3_message)
            if b.logo_file:
                logo_data = base64.b64decode(b.logo_file)
                await s3_wrapper.put_object(s3.IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            await db.commit()
        return tournament_id
          
@save_to_command_log
@dataclass
class EditTournamentCommand(Command[None]):
    body: EditTournamentRequestData
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_squad, game, logo FROM tournaments WHERE id = ?", (self.id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                is_squad, game, logo_path = row
            if b.logo_file:
                logo_path = f"/img/tournament_logos/{self.id}.png"
            elif b.remove_logo:
                logo_path = None
            if b.series_id:
                async with db.execute("SELECT id FROM tournament_series WHERE id = ?", (b.series_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise Problem("Series with provided ID cannot be found", status=404)
            # check for invalid body parameters
            if not is_squad and b.teams_allowed:
                raise Problem('Individual tournaments cannot have teams linked', status=400)
            if not b.teams_allowed and (b.teams_only or b.team_members_only):
                raise Problem('Non-team tournaments cannot have teams_only, team_members_only, min_representatives enabled', status=400)
            if not is_squad and (b.min_squad_size or b.max_squad_size or b.squad_tag_required or b.squad_name_required):
                raise Problem('Individual tournaments may not have settings for min_squad_size, max_squad_size, squad_tag_required, squad_name_required', status=400)
            if b.teams_allowed and (b.mii_name_required or b.host_status_required):
                raise Problem('Team tournaments cannot have mii_name_required, host_status_required, or require_single_fc enabled', status=400)
            if b.teams_allowed and (not b.squad_tag_required or not b.squad_name_required):
                raise Problem('Team tournaments must require a squad tag/name', status=400)
            if not b.series_id and b.use_series_logo:
                raise Problem('Cannot use series logo if no series is selected', status=400)
            if b.bagger_clause_enabled and not (game == 'mkw' and is_squad):
                raise Problem('Game must be set to MKW and it must be a squad tournament to use bagger clause', status=400)
            cursor = await db.execute("""UPDATE tournaments
                SET name = ?,
                series_id = ?,
                registrations_open = ?,
                date_start = ?,
                date_end = ?,
                use_series_description = ?,
                use_series_ruleset = ?,
                series_stats_include = ?,
                logo = ?,
                use_series_logo = ?,
                url = ?,
                registration_deadline = ?,
                registration_cap = ?,
                teams_allowed = ?,
                teams_only = ?,
                team_members_only = ?,
                min_squad_size = ?,
                max_squad_size = ?,
                squad_tag_required = ?,
                squad_name_required = ?,
                mii_name_required = ?,
                host_status_required = ?,
                checkins_enabled = ?,
                checkins_open = ?,
                min_players_checkin = ?,
                verification_required = ?,
                verified_fc_required = ?,
                is_viewable = ?,
                is_public = ?,
                is_deleted = ?,
                show_on_profiles = ?,
                min_representatives = ?
                WHERE id = ?""",
                (b.name, b.series_id, b.registrations_open, b.date_start, b.date_end, b.use_series_description, b.use_series_ruleset, b.series_stats_include,
                logo_path, b.use_series_logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_enabled, b.checkins_open,
                b.min_players_checkin, b.verification_required, b.verified_fc_required, b.is_viewable, b.is_public, b.is_deleted, b.show_on_profiles,
                b.min_representatives, self.id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No tournament found', status=404)
            
            s3_body = TournamentS3Fields(b.description, b.ruleset)
            s3_message = bytes(msgspec.json.encode(s3_body))
            await s3_wrapper.put_object(s3.TOURNAMENTS_BUCKET, f'{self.id}.json', s3_message)
            if b.logo_file:
                logo_filename = f"tournament_logos/{self.id}.png"
                logo_data = base64.b64decode(b.logo_file)
                await s3_wrapper.put_object(s3.IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            elif b.remove_logo:
                logo_filename = f"tournament_logos/{self.id}.png"
                await s3_wrapper.delete_object(s3.IMAGE_BUCKET, key=logo_filename)
            await db.commit()
            
@dataclass
class GetTournamentDataCommand(Command[GetTournamentRequestData]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            db.row_factory = Row
            async with db.execute("""SELECT * FROM tournaments WHERE id = ?""", (self.id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("No tournament found", status=404)
                t = msgspec.convert(row, type=TournamentDBFields, strict=False)
            async with db.execute("SELECT logo FROM tournaments WHERE id = ?", (self.id,)) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                logo = row[0]
            s3_body = await s3_wrapper.get_object(s3.TOURNAMENTS_BUCKET, f'{self.id}.json')
            if s3_body is None:
                raise Problem('No tournament found', status=404)
            s3_fields = msgspec.json.decode(s3_body, type=TournamentS3Fields)

            tournament_data = GetTournamentRequestData(id=self.id,
                                                       name=t.name,
                                                       game=t.game,
                                                       mode=t.mode,
                                                       series_id=t.series_id,
                                                       is_squad=t.is_squad,
                                                       registrations_open=t.registrations_open,
                                                       date_start=t.date_start,
                                                       date_end=t.date_end,
                                                       description=s3_fields.description,
                                                       use_series_description=t.use_series_description,
                                                       series_stats_include=t.series_stats_include,
                                                       logo=logo,
                                                       use_series_logo=t.use_series_logo,
                                                       url=t.url,
                                                       registration_deadline=t.registration_deadline,
                                                       registration_cap=t.registration_cap,
                                                       teams_allowed=t.teams_allowed,
                                                       teams_only=t.teams_only,
                                                       team_members_only=t.team_members_only,
                                                       min_squad_size=t.min_squad_size,
                                                       max_squad_size=t.max_squad_size,
                                                       squad_tag_required=t.squad_tag_required,
                                                       squad_name_required=t.squad_name_required,
                                                       mii_name_required=t.mii_name_required,
                                                       host_status_required=t.host_status_required,
                                                       checkins_enabled=t.checkins_enabled,
                                                       checkins_open=t.checkins_open,
                                                       min_players_checkin=t.min_players_checkin,
                                                       verification_required=t.verification_required,
                                                       verified_fc_required=t.verified_fc_required,
                                                       is_viewable=t.is_viewable,
                                                       is_public=t.is_public,
                                                       show_on_profiles=t.show_on_profiles,
                                                       require_single_fc=t.require_single_fc,
                                                       min_representatives=t.min_representatives,
                                                       bagger_clause_enabled=t.bagger_clause_enabled,
                                                       is_deleted=t.is_deleted,
                                                       use_series_ruleset=t.use_series_ruleset, 
                                                       organizer=t.organizer,
                                                       location=t.location,
                                                       ruleset=s3_fields.ruleset,
                                                       series_name=None,
                                                       series_url=None,
                                                       series_description=None,
                                                       series_ruleset=None)
            if tournament_data.series_id:
                s3_body = await s3_wrapper.get_object(s3.SERIES_BUCKET, f'{tournament_data.series_id}.json')
                if s3_body:
                    async with db.execute("SELECT name, url, logo FROM tournament_series WHERE id = ?", (tournament_data.series_id,)) as cursor:
                        row = await cursor.fetchone()
                        assert row is not None
                        series_name, series_url, series_logo = row
                    series = msgspec.json.decode(s3_body, type=SeriesS3Fields)
                    tournament_data.series_name = series_name
                    tournament_data.series_url = series_url
                    tournament_data.series_description = series.description
                    tournament_data.series_ruleset = series.ruleset
                    if tournament_data.use_series_logo:
                        tournament_data.logo = series_logo
                   
        return tournament_data

@dataclass
class GetTournamentListCommand(Command[TournamentList]):
    filter: TournamentFilter
    user: User | None

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []
            
            limit:int = 10
            offset:int = 0

            if filter.page is not None:
                offset = (filter.page - 1) * limit

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            if filter.name is not None:
                where_clauses.append(f"t.name LIKE ?")
                variable_parameters.append(f"%{filter.name}%")

            # if we are searching for tournaments which aren't public or viewable,
            # we need to perform permission checks on each tournament to see which ones
            # are viewable. so, we check tournament permissions, then series permissions,
            # then global permissions.
            if (not filter.is_public or not filter.is_viewable) and self.user:
                tournament_check = f"""
                    t.id IN (
                        SELECT DISTINCT ur.tournament_id
                        FROM tournament_roles r
                        JOIN user_tournament_roles ur ON ur.role_id = r.id
                        JOIN tournament_role_permissions rp ON rp.role_id = r.id
                        JOIN tournament_permissions p on rp.permission_id = p.id
                        WHERE ur.user_id = ? AND p.name = ?
                    )"""
                series_check = f"""
                    t.series_id IN (
                        SELECT DISTINCT ur.series_id
                        FROM series_roles r
                        JOIN user_series_roles ur ON ur.role_id = r.id
                        JOIN series_role_permissions rp ON rp.role_id = r.id
                        JOIN series_permissions p on rp.permission_id = p.id
                        WHERE ur.user_id = ? AND p.name = ?
                    )"""
                global_check = f"""
                    0 IN (
                        SELECT DISTINCT rp.is_denied
                        FROM roles r
                        JOIN user_roles ur ON ur.role_id = r.id
                        JOIN role_permissions rp ON rp.role_id = r.id
                        JOIN permissions p on rp.permission_id = p.id
                        WHERE ur.user_id = ? AND p.name = ?
                    )"""
                final_check = f"(t.is_public = 1 OR {tournament_check} OR {series_check} OR {global_check})"
                where_clauses.append(final_check)
                for _ in range(3):
                    variable_parameters.extend([self.user.id, tournament_permissions.VIEW_HIDDEN_TOURNAMENT])
            # we should only be searching for public and viewable tournaments if the first condition isn't met
            else:
                where_clauses.append("t.is_viewable = 1")
                where_clauses.append("t.is_public = 1")

            if filter.from_date:
                where_clauses.append("t.date_start >= ?")
                variable_parameters.append(filter.from_date)
            if filter.to_date:
                where_clauses.append("t.date_end < ?")
                variable_parameters.append(filter.to_date)

            append_equal_filter(filter.game, "t.game")
            append_equal_filter(filter.mode, "t.mode")
            append_equal_filter(filter.series_id, "t.series_id")
            append_equal_filter(filter.is_viewable, "t.is_viewable")
            append_equal_filter(filter.is_public, "t.is_public")
            

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            tournaments_query = f"""SELECT t.id, t.name, t.game, t.mode, t.date_start, t.date_end, t.is_squad, t.registrations_open, 
                                        t.teams_allowed, t.logo, t.use_series_logo, t.is_viewable, t.is_public,
                                        s.id, s.name, s.url, s.short_description, s.logo
                                        FROM tournaments t
                                        LEFT JOIN tournament_series s ON t.series_id = s.id
                                        {where_clause}
                                        ORDER BY date_start DESC, date_end ASC LIMIT ? OFFSET ?"""
            
            tournaments: list[TournamentDataBasic] = []
            async with db.execute(tournaments_query, (*variable_parameters, limit, offset)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (tournament_id, name, game, mode, date_start, date_end, is_squad, registrations_open,
                      teams_allowed, logo, use_series_logo, is_viewable, is_public,
                      series_id, series_name, series_url, series_short_description, series_logo) = row
                    if bool(use_series_logo):
                        logo = series_logo
                    tournaments.append(TournamentDataBasic(tournament_id, name, game, mode, date_start, date_end, series_id, series_name, series_url, series_short_description,
                        bool(is_squad), bool(registrations_open), bool(teams_allowed), logo, bool(use_series_logo), bool(is_viewable), bool(is_public)))

            count_query = f"SELECT COUNT(*) FROM tournaments t {where_clause}"
            page_count: int = 0
            tournament_count: int = 0
            async with db.execute(count_query, variable_parameters) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                tournament_count = row[0]

            page_count = int(tournament_count / limit) + (1 if tournament_count % limit else 0)

            return TournamentList(tournaments, tournament_count, page_count)

@dataclass
class CheckIfSquadTournament(Command[bool]):
    tournament_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
                return bool(is_squad)
            
@dataclass
class CheckTournamentVisibilityCommand(Command[bool]):
    tournament_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT is_viewable FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Tournament not found", status=404)
                is_viewable = row[0]
                return bool(is_viewable)
