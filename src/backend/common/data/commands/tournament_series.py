from dataclasses import asdict, dataclass
from typing import Any, Dict, List

import msgspec

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, Series, SeriesFilter, SeriesRequestData


@save_to_command_log
@dataclass
class CreateSeriesCommand(Command[None]):
    body: SeriesRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        # store minimal data about each series in the SQLite DB
        async with db_wrapper.connect() as db:
            cursor = await db.execute(
                "INSERT INTO tournament_series(name, url, game, mode, is_historical, is_public, description, logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (b.series_name, b.url, b.game, b.mode, b.is_historical, b.is_public, b.description, b.logo))
            series_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('series', f'{series_id}.json', s3_message)

@save_to_command_log
@dataclass
class EditSeriesCommand(Command[None]):
    body: SeriesRequestData
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        async with db_wrapper.connect() as db:
            cursor = await db.execute("""UPDATE tournament_series
                SET name = ?,
                url = ?,
                game = ?,
                mode = ?,
                is_historical = ?,
                is_public = ?,
                description = ?,
                logo = ?
                WHERE id = ?""",
                (b.series_name, b.url, b.game, b.mode, b.is_historical, b.is_public, b.description, b.logo, self.series_id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No series found', status=404)
            

            s3_data = await s3_wrapper.get_object('series', f'{self.series_id}.json')
            if s3_data is None:
                raise Problem("No series found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('series', f'{self.series_id}.json', s3_message)

            await db.commit()

@dataclass
class GetSeriesDataCommand(Command[Dict[Any, Any]]):
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        body = await s3_wrapper.get_object('series', f'{self.series_id}.json')
        if body is None:
            raise Problem('No series found', status=404)
        series_data = msgspec.json.decode(body)
        return series_data

@dataclass
class GetSeriesListCommand(Command[List[Series]]):
    filter: SeriesFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.mode, "mode")
            append_equal_filter(filter.is_public, "is_public")
            append_equal_filter(filter.is_historical, "is_historical")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"

            series_query = f"SELECT id, name, url, game, mode, is_historical, is_public, description, logo FROM tournament_series{where_clause}"

            series = []
            async with db.execute(series_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    series_id, series_name, url, game, mode, is_historical, is_public, description, logo = row
                    series.append(Series(series_id, series_name, url, game, mode, bool(is_historical), bool(is_public), description, logo))
            return series