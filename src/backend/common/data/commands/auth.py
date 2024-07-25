from dataclasses import dataclass
from common.auth import roles
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, User, ModNotifications, Permission, UserRole
from common.auth import permissions
from datetime import datetime, timezone
from typing import Iterable
from aiosqlite import Row

@dataclass 
class GetUserIdFromSessionCommand(Command[User | None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT user_id FROM sessions WHERE session_id = ?", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            user_id = int(row[0])
            async with db.execute("SELECT player_id FROM users WHERE id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            assert row is not None
            player_id = row[0]
            
            return User(user_id, player_id)

@dataclass
class CheckUserHasPermissionCommand(Command[bool]):
    user_id: int
    permission_name: str
    check_denied_only: bool = False
    team_id: int | None = None
    series_id: int | None = None
    tournament_id: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        timestamp = int(datetime.now(timezone.utc).timestamp())
        series_id = self.series_id

        async with db_wrapper.connect() as db:
            def check_perms(rows: Iterable[Row]):
                if len(rows) == 0:
                    # if check_denied_only is True, we only care about the absence of a denied permission,
                    # so an empty result set satisfies that
                    if self.check_denied_only:
                        return True
                    else:
                        return False
                # if we find an instance of the permission which isnt denied, we have the permission no matter what,
                # so just return True once we find one. otherwise, the permission must have been denied, so we return
                # False after iterating
                for row in rows:
                    is_denied = row[0]
                    if not is_denied:
                        return True
                return False
            
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
                    AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                    """, (self.user_id, self.tournament_id, self.permission_name, timestamp)) as cursor:
                    rows = await cursor.fetchall()

                if check_perms(rows):
                    return True
                
            if series_id:
                # check series roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM series_roles r
                    JOIN user_series_roles ur ON ur.role_id = r.id
                    JOIN series_role_permissions rp ON rp.role_id = r.id
                    JOIN series_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.series_id = ? AND p.name = ?
                    AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                    """, (self.user_id, self.series_id, self.permission_name, timestamp)) as cursor:
                    rows = await cursor.fetchall()

                if check_perms(rows):
                    return True
            
            if self.team_id:
                # check team roles
                async with db.execute("""
                    SELECT DISTINCT rp.is_denied
                    FROM team_roles r
                    JOIN user_team_roles ur ON ur.role_id = r.id
                    JOIN team_role_permissions rp ON rp.role_id = r.id
                    JOIN team_permissions p on rp.permission_id = p.id
                    WHERE ur.user_id = ? AND ur.team_id = ? AND p.name = ?
                    AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                    """, (self.user_id, self.team_id, self.permission_name, timestamp)) as cursor:
                    rows = await cursor.fetchall()

                if check_perms(rows):
                    return True
            
            #finally, check user roles
            async with db.execute("""
                SELECT DISTINCT rp.is_denied
                FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE ur.user_id = ? AND p.name = ?
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, self.permission_name, timestamp)) as cursor:
                rows = await cursor.fetchall()

            return check_perms(rows)
            
@dataclass
class IsValidSessionCommand(Command[bool]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id = ?)", (self.session_id,)) as cursor:
                row = await cursor.fetchone()

            return row is not None and bool(row[0])
        
@dataclass
class CreateSessionCommand(Command[None]):
    session_id: str
    user_id: int
    expires_on: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            command = "INSERT INTO sessions(session_id, user_id, expires_on) VALUES (?, ?, ?)"
            async with db.execute(command, (self.session_id, self.user_id, self.expires_on)) as cursor:
                rows_inserted = cursor.rowcount

            # TODO: Run queries to identify why session creation failed
            if rows_inserted != 1:
                raise Problem("Failed to create session")
                
            await db.commit()
            
@dataclass
class DeleteSessionCommand(Command[None]):
    session_id: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id, ))
            await db.commit()
                
@dataclass
class GetModNotificationsCommand(Command[ModNotifications]):
    user_roles: list[UserRole]

    async def handle(self, db_wrapper, s3_wrapper):
        mod_notifications = ModNotifications()
        string_perms = []
        for role in self.user_roles:
            for perm in role.permissions:
                string_perms.append(perm.name)

        async with db_wrapper.connect(readonly=True) as db:
            if permissions.MANAGE_TEAMS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM teams WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_teams += row[0]
                # pending roster requests where team is already approved
                async with db.execute("""SELECT COUNT(r.id) FROM team_rosters r JOIN teams t ON r.team_id = t.id 
                                      WHERE t.approval_status='approved' AND r.approval_status='pending'""") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_teams += row[0]
                async with db.execute("SELECT COUNT(id) FROM team_edit_requests WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
                async with db.execute("SELECT COUNT(id) FROM roster_edit_requests WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
            if permissions.MANAGE_TRANSFERS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE is_accepted = 1 AND approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_transfers = row[0]
        return mod_notifications