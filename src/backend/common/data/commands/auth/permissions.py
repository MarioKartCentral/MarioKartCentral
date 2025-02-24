from aiosqlite import Row
from dataclasses import dataclass
from typing import Iterable
from common.data.commands import Command
from common.data.models import *

@dataclass
class CheckUserHasPermissionCommand(Command[bool]):
    user_id: int
    permission_name: str
    check_denied_only: bool = False
    team_id: int | None = None
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        series_id = self.series_id

        async with db_wrapper.connect() as db:
            allowed_permission_exists = False
            def check_perms(rows: Iterable[Row]):
                num_rows = sum(1 for r in rows) # type: ignore
                if num_rows == 0:
                    return None
                # if we find an instance of the permission which isnt denied, we have the permission no matter what,
                # so just return True once we find one. otherwise, the permission must have been denied, so we return
                # False after iterating
                for row in rows:
                    is_denied = row[0]
                    if is_denied:
                        return False
                return True
            
            if self.tournament_id:
                # if tournament is part of a series, we want to find out its id so we can check series permissions also
                if not series_id:
                    async with db.execute("SELECT series_id FROM tournaments WHERE id = ?", (self.tournament_id,)) as cursor:
                        row = await cursor.fetchone()
                        if not row:
                            raise Problem("Tournament not found", status=400)
                        series_id = row[0]

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
                if perm_check is False:
                    return False
                if perm_check is True:
                    allowed_permission_exists = True
                
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
                if perm_check is False:
                    return False
                if perm_check is True:
                    allowed_permission_exists = True
            
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
                if perm_check is False:
                    return False
                if perm_check is True:
                    allowed_permission_exists = True
            
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
            # if the permission isn't explicitly granted in user roles,
            # see if it's been granted in another role type, and if it has,
            # return true. otherwise, if check_denied_only is true, 
            # we only care about the absence of a denied permission, so return true.
            # if check_denied_only is false, we haven't been explicitly granted
            # the permission, so return false.
            if perm_check is None:
                if allowed_permission_exists:
                    return True
                return self.check_denied_only
            return perm_check