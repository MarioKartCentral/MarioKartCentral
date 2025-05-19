from dataclasses import dataclass
from typing import Any

import msgspec

from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, Series, SeriesBasic, SeriesFilter, EditSeriesRequestData, CreateSeriesRequestData, SeriesS3Fields, User
from common.auth import series_permissions
import common.data.s3 as s3
import base64

@save_to_command_log
@dataclass
class CreateSeriesCommand(Command[None]):
    body: CreateSeriesRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        # store minimal data about each series in the SQLite DB
        async with db_wrapper.connect() as db:
            cursor = await db.execute(
                """INSERT INTO tournament_series(name, url, display_order, game, mode, is_historical, is_public, short_description, logo, organizer, location, discord_invite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (b.series_name, b.url, b.display_order, b.game, b.mode, b.is_historical, b.is_public, b.short_description, None,
                 b.organizer, b.location, b.discord_invite))
            series_id = cursor.lastrowid
            logo_filename = f"series_logos/{series_id}.png"
            logo_path = f"/img/{logo_filename}"
            if b.logo_file:
                await db.execute("UPDATE tournament_series SET logo = ? WHERE id = ?", (logo_path, series_id))

            s3_body = SeriesS3Fields(b.description, b.ruleset)
            s3_message = bytes(msgspec.json.encode(s3_body))
            await s3_wrapper.put_object(s3.SERIES_BUCKET, f'{series_id}.json', s3_message)
            if b.logo_file:
                logo_data = base64.b64decode(b.logo_file)
                await s3_wrapper.put_object(s3.IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            await db.commit()

@save_to_command_log
@dataclass
class EditSeriesCommand(Command[None]):
    body: EditSeriesRequestData
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT logo FROM tournament_series WHERE id = ?", (self.series_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Series not found", status=404)
                logo_path = row[0]
            if b.logo_file:
                logo_path = f"/img/series_logos/{self.series_id}.png"
            elif b.remove_logo:
                logo_path = None
            await db.execute("""UPDATE tournament_series
                SET name = ?,
                url = ?,
                display_order = ?,
                game = ?,
                mode = ?,
                is_historical = ?,
                is_public = ?,
                short_description = ?,
                logo = ?,
                organizer = ?,
                location = ?,
                discord_invite = ?
                WHERE id = ?""",
                (b.series_name, b.url, b.display_order, b.game, b.mode, b.is_historical, b.is_public, b.short_description, logo_path, b.organizer, b.location,
                 b.discord_invite, self.series_id))

            s3_body = SeriesS3Fields(b.description, b.ruleset)
            s3_message = bytes(msgspec.json.encode(s3_body))
            await s3_wrapper.put_object(s3.SERIES_BUCKET, f'{self.series_id}.json', s3_message)
            if b.logo_file:
                logo_filename = f"series_logos/{self.series_id}.png"
                logo_data = base64.b64decode(b.logo_file)
                await s3_wrapper.put_object(s3.IMAGE_BUCKET, key=logo_filename, body=logo_data, acl="public-read")
            elif b.remove_logo:
                logo_filename = f"series_logos/{self.series_id}.png"
                await s3_wrapper.delete_object(s3.IMAGE_BUCKET, key=logo_filename)
            await db.commit()

@dataclass
class GetSeriesDataCommand(Command[Series]):
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT id, name, url, display_order, game, mode, is_historical, is_public, short_description,
                                    logo, organizer, location, discord_invite FROM tournament_series WHERE id = ?""", (self.series_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Series not found", status=404)
                series_id, name, url, display_order, game, mode, is_historical, is_public, short_description, logo, organizer, location, discord_invite = row
        body = await s3_wrapper.get_object(s3.SERIES_BUCKET, f'{self.series_id}.json')
        if body is None:
            raise Problem('No series found', status=404)
        s3_data = msgspec.json.decode(body, type=SeriesS3Fields)
        series = Series(series_id, name, url, display_order, game, mode, bool(is_historical), bool(is_public),
                        short_description, logo, organizer, location, discord_invite, s3_data.description, s3_data.ruleset)
        return series

@dataclass
class GetSeriesListCommand(Command[list[SeriesBasic]]):
    filter: SeriesFilter
    user: User | None

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def append_equal_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)
            
            def append_like_filter(filter_value: Any, column_name: str):
                if filter_value is not None:
                    where_clauses.append(f"LOWER({column_name}) LIKE ?")
                    variable_parameters.append(f"%{filter_value}%")

            append_equal_filter(filter.game, "game")
            append_equal_filter(filter.mode, "mode")
            append_equal_filter(filter.is_historical, "is_historical")
            append_like_filter(filter.name, "name")

            if not filter.is_public and self.user:
                series_check = f"""
                    id IN (
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
                final_check = f"(is_public = 1 OR {series_check} OR {global_check})"
                where_clauses.append(final_check)
                variable_parameters.extend([self.user.id, series_permissions.VIEW_HIDDEN_SERIES, self.user.id, series_permissions.VIEW_HIDDEN_SERIES])
            else:
                where_clauses.append("is_public = 1")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"

            series_query = f"""SELECT id, name, url, display_order, game, mode, is_historical, is_public, short_description, logo, organizer, location,
                                    discord_invite 
                                    FROM tournament_series {where_clause} ORDER BY display_order ASC"""

            series: list[SeriesBasic] = []
            async with db.execute(series_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    (series_id, series_name, url, display_order, game, mode, is_historical, 
                     is_public, short_description, logo, organizer, location, discord_invite) = row
                    series.append(SeriesBasic(series_id, series_name, url, display_order, game, mode, 
                                              bool(is_historical), bool(is_public), short_description, logo, organizer, location,
                                              discord_invite))
            return series
        
@dataclass
class CheckSeriesVisibilityCommand(Command[bool]):
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT is_public FROM tournament_series WHERE id = ?", (self.series_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Series not found", status=404)
                is_viewable = row[0]
                return bool(is_viewable)