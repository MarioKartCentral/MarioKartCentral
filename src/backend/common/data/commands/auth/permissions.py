from aiosqlite import Row
from dataclasses import dataclass
from typing import Iterable
from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *

@dataclass
class CheckUserHasPermissionCommand(Command[bool]):
    user_id: int
    permission_name: str
    check_denied_only: bool = False
    team_id: int | None = None
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect() as db:
            def check_perms(rows: Iterable[Row]):
                # if we find an instance of the permission which is denied, always just return False
                has_row = False
                for row in rows:
                    has_row = True
                    is_denied = row[0]
                    if is_denied:
                        return False
                return True if has_row else None
            
            #finally, check user roles
            async with db.execute("""
                SELECT DISTINCT rp.is_denied
                FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE ur.user_id = ? AND p.name = ?
                """, (self.user_id, self.permission_name)) as cursor:
                rows = await cursor.fetchall()

            perm_check = check_perms(rows)
            if perm_check is not None:
                return perm_check
            
            series_id = self.series_id
            # if tournament is part of a series, we want to find out its id so we can check series permissions also
            if self.tournament_id and not series_id:
                async with db.execute("SELECT series_id FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise Problem("Tournament not found", status=400)
                    series_id = row[0]

            if series_id:
                # check series roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM series_roles r
                    JOIN user_series_roles ur ON ur.role_id = r.id
                    JOIN series_role_permissions rp ON rp.role_id = r.id
                    JOIN series_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.series_id = ? AND p.name = ?
                    """, (self.user_id, series_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()

                perm_check = check_perms(rows)
                if perm_check is not None:
                    return perm_check
            
            if self.tournament_id:
                # check tournament roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM tournament_roles r
                    JOIN user_tournament_roles ur ON ur.role_id = r.id
                    JOIN tournament_role_permissions rp ON rp.role_id = r.id
                    JOIN tournament_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.tournament_id = ? AND p.name = ?
                    """, (self.user_id, self.tournament_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()
                perm_check = check_perms(rows)
                if perm_check is not None:
                    return perm_check
                
            if self.team_id:
                # check team roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.team_id = ? AND p.name = ?
                    """, (self.user_id, self.team_id, self.permission_name)) as cursor:
                    rows = await cursor.fetchall()

                perm_check = check_perms(rows)
                if perm_check is not None:
                    return perm_check
                
            # if we haven't found any instance of the permission at this point,
            # return true if we're only checking for denied permissions, otherwise
            # false since the permission doesn't exist
            return self.check_denied_only
        