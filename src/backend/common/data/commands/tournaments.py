from dataclasses import asdict, dataclass
from typing import List

import msgspec

from common.data.commands import Command
from common.data.models import *


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

        # store minimal data about each tournament in the SQLite DB
        async with db_wrapper.connect() as db:
            
            cursor = await db.execute(
                """INSERT INTO tournaments(
                    name, game, mode, series_id, is_squad, registrations_open, date_start, date_end, description, use_series_description, series_stats_include,
                    logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size, max_squad_size, squad_tag_required,
                    squad_name_required, mii_name_required, host_status_required, checkins_open, min_players_checkin, verified_fc_required, is_viewable, is_public,
                    show_on_profiles, require_single_fc, min_representatives
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.tournament_name, b.game, b.mode, b.series_id, b.is_squad, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description,
                b.series_stats_include, b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open, b.min_players_checkin,
                b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, b.require_single_fc, b.min_representatives))
            tournament_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('tournaments', f'{tournament_id}.json', s3_message)
            
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
                verified_fc_required = ?,
                is_viewable = ?,
                is_public = ?,
                show_on_profiles = ?,
                min_representatives = ?
                WHERE id = ?""",
                (b.tournament_name, b.series_id, b.registrations_open, b.date_start, b.date_end, b.description, b.use_series_description, b.series_stats_include,
                b.logo, b.url, b.registration_deadline, b.registration_cap, b.teams_allowed, b.teams_only, b.team_members_only, b.min_squad_size,
                b.max_squad_size, b.squad_tag_required, b.squad_name_required, b.mii_name_required, b.host_status_required, b.checkins_open,
                b.min_players_checkin, b.verified_fc_required, b.is_viewable, b.is_public, b.show_on_profiles, b.min_representatives, self.id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No tournament found', status=404)
            

            s3_data = await s3_wrapper.get_object('tournaments', f'{self.id}.json')
            if s3_data is None:
                raise Problem("No tournament found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('tournaments', f'{self.id}.json', s3_message)

            await db.commit()

        
    
@dataclass
class GetTournamentDataCommand(Command[CreateTournamentRequestData]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        body = await s3_wrapper.get_object('tournaments', f'{self.id}.json')
        if body is None:
            raise Problem('No tournament found', status=404)
        tournament_data = msgspec.json.decode(body, type=CreateTournamentRequestData)
        return tournament_data

@dataclass
class GetTournamentListCommand(Command[List[TournamentDataMinimal]]):
    filter: TournamentFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        is_minimal = filter.is_minimal
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
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
                tournaments_query = f"SELECT id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, description, logo FROM tournaments{where_clause}"
            
            tournaments = []
            async with db.execute(tournaments_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    if is_minimal:
                        tournament_id, name, game, mode, date_start, date_end = row
                        tournaments.append(TournamentDataMinimal(tournament_id, name, game, mode, date_start, date_end))
                    else:
                        tournament_id, name, game, mode, date_start, date_end, series_id, is_squad, registrations_open, description, logo = row
                        tournaments.append(TournamentDataBasic(tournament_id, name, game, mode, date_start, date_end, series_id,
                            bool(is_squad), bool(registrations_open), description, logo))
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