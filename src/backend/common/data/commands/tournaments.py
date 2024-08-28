from dataclasses import asdict, dataclass

import msgspec

from common.data.commands import Command, save_to_command_log
from common.data.models import *
import common.data.s3 as s3


@save_to_command_log
@dataclass
class CreateTournamentCommand(Command[None]):
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

        # store minimal data about each tournament in the SQLite DB
        async with db_wrapper.connect() as db:
            
            cursor = await db.execute(
                """INSERT INTO tournaments(
                    name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, use_series_description, series_stats_include,
                    logo, use_series_logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                    squad_name_required, mii_name_required, host_status_required, checkins_open, min_players_checkin, verification_required, verified_fc_required, is_viewable,
                    is_public, is_deleted, show_on_profiles, require_single_fc, min_representatives
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.tournament_name, b.game, b.mode, b.series_id, b.is_squad, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description,
                b.series_stats_include, b.logo, b.use_series_logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open, b.min_players_checkin, b.verification_required,
                b.verified_fc_required, b.is_viewable, b.is_public, False, b.show_on_profiles, b.require_single_fc, b.min_representatives))
            tournament_id = cursor.lastrowid
            await db.commit()
        # make sure tournament ID is at the top of the s3's body
        s3_body = {'id': tournament_id, 'is_deleted': False}
        s3_body.update(asdict(self.body))
        s3_message = bytes(msgspec.json.encode(s3_body))
        await s3_wrapper.put_object(s3.TOURNAMENTS_BUCKET, f'{tournament_id}.json', s3_message)
            
@save_to_command_log
@dataclass
class EditTournamentCommand(Command[None]):
    body: EditTournamentRequestData
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_squad FROM tournaments WHERE id = ?", (self.id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Tournament not found", status=404)
                is_squad = row[0]
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
            cursor = await db.execute("""UPDATE tournaments
                SET name = ?,
                series_id = ?,
                registrations_open = ?,
                date_start = ?,
                date_end = ?,
                description = ?,
                use_series_description = ?,
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
                (b.tournament_name, b.series_id, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description, b.series_stats_include,
                b.logo, b.use_series_logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open,
                b.min_players_checkin, b.verification_required, b.verified_fc_required, b.is_viewable, b.is_public, b.is_deleted, b.show_on_profiles,
                b.min_representatives, self.id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No tournament found', status=404)
            

            s3_data = await s3_wrapper.get_object(s3.TOURNAMENTS_BUCKET, f'{self.id}.json')
            if s3_data is None:
                raise Problem("No tournament found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object(s3.TOURNAMENTS_BUCKET, f'{self.id}.json', s3_message)

            await db.commit()

@dataclass
class GetTournamentDataCommand(Command[GetTournamentRequestData]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        body = await s3_wrapper.get_object(s3.TOURNAMENTS_BUCKET, f'{self.id}.json')
        if body is None:
            raise Problem('No tournament found', status=404)
        tournament_data = msgspec.json.decode(body, type=GetTournamentRequestData)
        
        if tournament_data.series_id is not None:
            async with db_wrapper.connect(readonly=True) as db:
                async with db.execute("SELECT name, url, description, ruleset, logo FROM tournament_series WHERE id = ?", (tournament_data.series_id,)) as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    series_name, series_url, series_description, series_ruleset, logo = row
                    tournament_data.series_name = series_name
                    tournament_data.series_url = series_url
                    tournament_data.series_description = series_description
                    tournament_data.series_ruleset = series_ruleset
                    if tournament_data.use_series_logo:
                        tournament_data.logo = logo
        return tournament_data

@dataclass
class GetTournamentListCommand(Command[list[TournamentDataMinimal]]):
    filter: TournamentFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        is_minimal = filter.is_minimal
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            if filter.name is not None:
                where_clauses.append(f"name LIKE ?")
                variable_parameters.append(f"%{filter.name}%")

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.mode, "mode")
            append_equal_filter(filter.series_id, "series_id")
            append_equal_filter(filter.is_public, "is_public")
            append_equal_filter(filter.is_viewable, "is_viewable")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"
            if is_minimal:
                tournaments_query = f"SELECT id, name, game, mode, date_start, date_end FROM tournaments{where_clause}"
            else:
                tournaments_query = f"SELECT id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, teams_allowed, description, logo, use_series_logo FROM tournaments{where_clause}"
            
            tournaments: list[TournamentDataMinimal | TournamentDataBasic] = []
            series_ids: list[int] = []
            series_info = {}
            async with db.execute(tournaments_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    if is_minimal:
                        tournament_id, name, game, mode, date_start, date_end = row
                        tournaments.append(TournamentDataMinimal(tournament_id, name, game, mode, date_start, date_end))
                    else:
                        tournament_id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, teams_allowed, description, logo, use_series_logo = row
                        tournaments.append(TournamentDataBasic(tournament_id, name, game, mode, date_start, date_end, series_id, None, None, None,
                            bool(is_squad), bool(registrations_open), bool(teams_allowed), description, logo, bool(use_series_logo)))
                        if series_id is not None:
                            series_ids.append(series_id)
            # get relevant info about tournament series for all tournaments part of one
            if len(series_ids) > 0:
                series_set = set(series_ids)
                series_query = f"({','.join([str(s) for s in series_set])})"
                async with db.execute(f"SELECT id, name, url, description, logo FROM tournament_series WHERE id IN {series_query}") as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        series_id, name, url, description, logo = row
                        series_info[series_id] = {'name': name, 'url': url, 'description': description, 'logo': logo}
                for tournament in tournaments:
                    if not isinstance(tournament, TournamentDataBasic) or tournament.series_id is None:
                        continue
                    if tournament.use_series_logo:
                        tournament.logo = series_info[tournament.series_id]['logo']
                    tournament.series_name = series_info[tournament.series_id]['name']
                    tournament.series_url = series_info[tournament.series_id]['url']
                    tournament.series_description = series_info[tournament.series_id]['description']
            return tournaments
        
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