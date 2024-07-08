from dataclasses import dataclass
from common.auth import roles
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, User, ModNotifications, TeamPermissions, SeriesPermissions
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

    async def handle(self, db_wrapper, s3_wrapper):
        timestamp = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
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
        
@dataclass
class CheckUserHasTeamPermissionCommand(Command[bool]):
    user_id: int
    team_id: int
    permission_name: str
    check_denied_only: bool = False

    async def handle(self, db_wrapper, s3_wrapper):
        timestamp = int(datetime.now(timezone.utc).timestamp())
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

            # check user roles
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
class GetUserWithPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM roles r
                JOIN user_roles ur ON ur.role_id = r.id
                JOIN users u on ur.user_id = u.id
                JOIN sessions s on s.user_id = u.id
                JOIN role_permissions rp on rp.role_id = r.id
                JOIN permissions p on rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ?
                LIMIT 1""", (self.session_id, self.permission_name)) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            return User(int(row[0]), row[1])
        
@dataclass
class GetUserWithTeamPermissionFromSessionCommand(Command[User | None]):
    session_id: str
    permission_name: str
    team_id: int
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("""
                SELECT u.id, u.player_id FROM team_roles r
                JOIN user_team_roles ur ON ur.role_id = r.id
                JOIN users u ON ur.user_id = u.id
                JOIN sessions s ON s.user_id = u.id
                JOIN team_role_permissions rp ON rp.role_id = r.id
                JOIN team_permissions p ON rp.permission_id = p.id
                WHERE s.session_id = ? AND p.name = ? AND ur.team_id = ?
                LIMIT 1""", (self.session_id, self.permission_name, self.team_id)) as cursor:
                row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return User(int(row[0]), row[1])
        
@dataclass
class CheckPermissionsCommand(Command[tuple[list[str], list[TeamPermissions], list[SeriesPermissions]]]):
    user_id: int
    permissions: list[str]
    check_team_perms: bool
    check_series_perms: bool

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            valid_perms: list[str] = []
            async with db.execute(f"""
                SELECT DISTINCT p.name
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ? AND p.name IN ({','.join([f"?" for _ in self.permissions])})
                """, (self.user_id, *self.permissions)) as cursor:
                rows = await cursor.fetchall()
                valid_perms = [row[0] for row in rows]
            team_perms = []
            # only check team permissions if we are on a page that needs them
            if self.check_team_perms:
                async with db.execute(f"""
                    SELECT ur.team_id, p.name
                    FROM user_team_roles ur
                    JOIN team_role_permissions rp ON ur.role_id = rp.role_id
                    JOIN team_permissions p ON rp.permission_id = p.id
                    WHERE ur.user_id = ?
                    """, (self.user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    team_perm_dict: dict[int, list[str]] = {}
                    for row in rows:
                        team_id, perm = row
                        if team_id not in team_perm_dict:
                            team_perm_dict[team_id] = []
                        team_perm_dict[team_id].append(perm)
                    team_perms = [TeamPermissions(team_id, perms) for team_id, perms in team_perm_dict.items()]
            series_perms = []
            if self.check_series_perms:
                async with db.execute(f"""
                    SELECT ur.series_id, p.name
                    FROM user_series_roles ur
                    JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                    JOIN team_permissions p ON rp.permission_id = p.id
                    WHERE ur.user_id = ?
                    """, (self.user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    series_perm_dict: dict[int, list[str]] = {}
                    for row in rows:
                        series_id, perm = row
                        if series_id not in series_perm_dict:
                            series_perm_dict[series_id] = []
                        series_perm_dict[series_id].append(perm)
                    series_perms = [SeriesPermissions(series_id, perms) for series_id, perms in series_perm_dict.items()]
        return valid_perms, team_perms, series_perms
            
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

@save_to_command_log
@dataclass
class GrantRoleCommand(Command[None]):
    granter_user_id: int
    target_user_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        # For now, the rules about which roles can grant other roles is defined here, but we could move it to  the database
        # in the future.
        if self.role in [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]:
            allowed_roles = [roles.SUPER_ADMINISTRATOR]
        else:
            allowed_roles = [roles.SUPER_ADMINISTRATOR, roles.ADMINISTRATOR]

        allowed_role_ids = [roles.id_by_default_role[role] for role in allowed_roles]

        async with db_wrapper.connect() as db:
            async with db.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM roles r
                    JOIN user_roles ur ON ur.role_id = r.id
                    JOIN users u on ur.user_id = u.id
                    WHERE u.id = ? AND r.id IN ({','.join(map(str, allowed_role_ids))})
                )""", (self.granter_user_id,)) as cursor:
                row = await cursor.fetchone()
                can_grant = row is not None and bool(row[0])

            if not can_grant:
                raise Problem("Not authorized to grant role", status=401)

            try:
                async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                    row = await cursor.fetchone()
                    role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)

                await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)", (self.target_user_id, role_id))
                await db.commit()
            except Exception:
                async with db.execute("SELECT EXISTS(SELECT 1 FROM users where id = ?)", (self.target_user_id,)) as cursor:
                    row = await cursor.fetchone()
                    user_exists = row is not None

                if not user_exists:
                    raise Problem("User not found", status=404)
                else:
                    raise Problem("Unexpected error")
                
@dataclass
class GetModNotificationsCommand(Command[ModNotifications]):
    valid_perms: list[str]

    async def handle(self, db_wrapper, s3_wrapper):
        mod_notifications = ModNotifications()
        async with db_wrapper.connect(readonly=True) as db:
            if permissions.MANAGE_TEAMS in self.valid_perms:
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
            if permissions.MANAGE_TRANSFERS in self.valid_perms:
                async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE is_accepted = 1 AND approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_transfers = row[0]
        return mod_notifications