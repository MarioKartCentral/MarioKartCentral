from dataclasses import dataclass
from common.auth import permissions, team_permissions, series_permissions, tournament_permissions
from common.data.commands import Command, save_to_command_log
from common.data.models import *
from common.auth.roles import BANNED
from datetime import datetime, timezone

from common.data.models.roles import TeamRoleInfo

@dataclass
class ListRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            # ban info can be retrieved in its own endpoint
            async with db.execute(f"SELECT id, name, position FROM roles WHERE name != '{BANNED}'") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles
        
@dataclass
class ListTeamRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            async with db.execute(f"SELECT id, name, position FROM team_roles") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles
        
@dataclass
class ListSeriesRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            async with db.execute(f"SELECT id, name, position FROM series_roles") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles
        
@dataclass
class ListTournamentRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            async with db.execute(f"SELECT id, name, position FROM tournament_roles") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles
        
@dataclass
class GetRoleInfoCommand(Command[RoleInfo]):
    role_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute(f"""
                SELECT p.name, rp.is_denied
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                """, (self.role_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    permission_name, is_denied = row
                    permissions.append(Permission(permission_name, is_denied))
            
            players: list[RolePlayer] = []
            async with db.execute(f"""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id, ur.expires_on
                FROM user_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ?
                """, (self.role_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on))
            role_info = RoleInfo(self.role_id, role_name, position, permissions, players)
            return role_info
        
@dataclass
class GetTeamRoleInfoCommand(Command[TeamRoleInfo]):
    role_id: int
    team_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> TeamRoleInfo:
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM team_roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute(f"""
                SELECT p.name, rp.is_denied
                FROM team_permissions p
                JOIN team_role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                """, (self.role_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    permission_name, is_denied = row
                    permissions.append(Permission(permission_name, is_denied))
            
            players: list[RolePlayer] = []
            async with db.execute(f"""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id, ur.expires_on
                FROM user_team_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ?  AND ur.team_id = ?
                """, (self.role_id, self.team_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on))
            role_info = TeamRoleInfo(self.role_id, role_name, position, permissions, players, self.team_id)
            return role_info
        
@dataclass
class GetSeriesRoleInfoCommand(Command[SeriesRoleInfo]):
    role_id: int
    series_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM series_roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute(f"""
                SELECT p.name, rp.is_denied
                FROM series_permissions p
                JOIN series_role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                """, (self.role_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    permission_name, is_denied = row
                    permissions.append(Permission(permission_name, is_denied))
            
            players: list[RolePlayer] = []
            async with db.execute(f"""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id, ur.expires_on
                FROM user_series_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ? AND ur.series_id = ?
                """, (self.role_id, self.series_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on))
            role_info = SeriesRoleInfo(self.role_id, role_name, position, permissions, players, self.series_id)
            return role_info
        
@dataclass
class GetTournamentRoleInfoCommand(Command[TournamentRoleInfo]):
    role_id: int
    tournament_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM tournament_roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute(f"""
                SELECT p.name, rp.is_denied
                FROM tournament_permissions p
                JOIN tournament_role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                """, (self.role_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    permission_name, is_denied = row
                    permissions.append(Permission(permission_name, is_denied))
            
            players: list[RolePlayer] = []
            async with db.execute(f"""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id, ur.expires_on
                FROM user_tournament_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ? AND ur.tournament_id = ?
                """, (self.role_id, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id, expires_on))
            role_info = TournamentRoleInfo(self.role_id, role_name, position, permissions, players, self.tournament_id)
            return role_info
                
@dataclass
class GetUserRolePermissionsCommand(Command[tuple[list[UserRole], list[TeamRole], list[SeriesRole], list[TournamentRole]]]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            # user roles
            role_dict: dict[int, UserRole] = {}
            async with db.execute("""
                SELECT DISTINCT r.id, r.name, r.position, ur.expires_on
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    role_id, name, position, expires_on = row
                    role_dict[role_id] = UserRole(role_id, name, position, expires_on, [])
                    
            async with db.execute("""
                SELECT DISTINCT ur.role_id, p.name, rp.is_denied
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                for row in rows:
                    role_id, perm_name, is_denied = row
                    role_dict[role_id].permissions.append(Permission(perm_name, is_denied))
            user_role_list = list(role_dict.values())


            # team roles
            team_roles: list[TeamRole] = []
            team_role_permissions: dict[int, list[Permission]] = {}
            async with db.execute("""
                SELECT DISTINCT r.id, r.name, r.position, ur.expires_on, ur.team_id
                FROM user_team_roles ur
                JOIN team_roles r ON ur.role_id = r.id
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                for row in rows:
                    role_id, name, position, expires_on, team_id = row
                    team_roles.append(TeamRole(role_id, name, position, expires_on, [], team_id))
                    # set the list of permissions for the role with this id to be empty
                    team_role_permissions[role_id] = []

            async with db.execute("""
                SELECT DISTINCT ur.role_id, p.name, rp.is_denied
                FROM user_team_roles ur
                JOIN team_role_permissions rp ON ur.role_id = rp.role_id
                JOIN team_permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                # since we can have the same role in multiple teams potentially, we just
                # keep a single list of permissions for each role then iterate through
                # our team roles and set the permissions field to those lists to save work
                for row in rows:
                    role_id, perm_name, is_denied = row
                    team_role_permissions[role_id].append(Permission(perm_name, is_denied))
                for role in team_roles:
                    role.permissions = team_role_permissions[role.id]


            # series roles
            series_roles: list[SeriesRole] = []
            series_role_permissions: dict[int, list[Permission]] = {}
            async with db.execute("""
                SELECT DISTINCT r.id, r.name, r.position, ur.expires_on, ur.series_id
                FROM user_series_roles ur
                JOIN series_roles r ON ur.role_id = r.id
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                for row in rows:
                    role_id, name, position, expires_on, series_id = row
                    series_roles.append(SeriesRole(role_id, name, position, expires_on, [], series_id))
                    # set the list of permissions for the role with this id to be empty
                    series_role_permissions[role_id] = []

            async with db.execute("""
                SELECT DISTINCT ur.role_id, p.name, rp.is_denied
                FROM user_series_roles ur
                JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                JOIN series_permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                # since we can have the same role in multiple series potentially, we just
                # keep a single list of permissions for each role then iterate through
                # our series roles and set the permissions field to those lists to save work
                for row in rows:
                    role_id, perm_name, is_denied = row
                    series_role_permissions[role_id].append(Permission(perm_name, is_denied))
                for role in series_roles:
                    role.permissions = series_role_permissions[role.id]


            # tournament roles
            tournament_roles: list[TournamentRole] = []
            tournament_role_permissions: dict[int, list[Permission]] = {}
            async with db.execute("""
                SELECT DISTINCT r.id, r.name, r.position, ur.expires_on, ur.tournament_id
                FROM user_tournament_roles ur
                JOIN tournament_roles r ON ur.role_id = r.id
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                for row in rows:
                    role_id, name, position, expires_on, tournament_id = row
                    tournament_roles.append(TournamentRole(role_id, name, position, expires_on, [], tournament_id))
                    # set the list of permissions for the role with this id to be empty
                    tournament_role_permissions[role_id] = []

            async with db.execute("""
                SELECT DISTINCT ur.role_id, p.name, rp.is_denied
                FROM user_tournament_roles ur
                JOIN tournament_role_permissions rp ON ur.role_id = rp.role_id
                JOIN tournament_permissions p ON rp.permission_id = p.id 
                WHERE ur.user_id = ?
                """, (self.user_id,)) as cursor:
                rows = await cursor.fetchall()

                # since we can have the same role in multiple tournaments potentially, we just
                # keep a single list of permissions for each role then iterate through
                # our tournament roles and set the permissions field to those lists to save work
                for row in rows:
                    role_id, perm_name, is_denied = row
                    tournament_role_permissions[role_id].append(Permission(perm_name, is_denied))
                for role in tournament_roles:
                    role.permissions = tournament_role_permissions[role.id]

            return user_role_list, team_roles, series_roles, tournament_roles
            
@save_to_command_log
@dataclass
class GrantRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if self.expires_on and self.expires_on < timestamp:
                raise Problem("Role cannot expire in the past", status=400)
            
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_roles WHERE user_id = ? AND role_id = ?", (target_user_id, role_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem(f"Player already has role {self.role}", status=400)
        
            # to have permission to grant a role, we should have a role which is both higher
            # in the role hierarchy than the role we wish to grant, and has the MANAGE_USER_ROLES
            # permission.
            async with db.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM roles r1
                    JOIN user_roles ur ON ur.role_id = r1.id
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.id
                    JOIN roles r2
                    WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                    AND rp.is_denied = 0 AND p.name = ?
                )
                """, (self.granter_user_id, self.role, permissions.MANAGE_USER_ROLES)) as cursor:
                row = await cursor.fetchone()
                can_grant = row is not None and bool(row[0])

            if not can_grant:
                raise Problem("Not authorized to grant role", status=401)

            try:
                await db.execute("INSERT INTO user_roles(user_id, role_id, expires_on) VALUES (?, ?, ?)", (target_user_id, role_id, self.expires_on))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class GrantTeamRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    team_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if self.expires_on and self.expires_on < timestamp:
                raise Problem("Role cannot expire in the past", status=400)
            
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM team_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_team_roles WHERE user_id = ? AND role_id = ? AND team_id = ?", (target_user_id, role_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem(f"Player already has role {self.role}", status=400)
            
            # if we have the team_permissions.MANAGE_TEAM_ROLES global permission, bypass team role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.granter_user_id, team_permissions.MANAGE_TEAM_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to grant a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to grant, and has the MANAGE_TEAM_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM team_roles r1
                        JOIN user_team_roles ur ON ur.role_id = r1.id
                        JOIN team_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN team_permissions p ON rp.permission_id = p.id
                        JOIN team_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.team_id = ?
                    )
                    """, (self.granter_user_id, self.role, team_permissions.MANAGE_TEAM_ROLES, self.team_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to grant role", status=401)

            try:
                await db.execute("INSERT INTO user_team_roles(user_id, role_id, team_id, expires_on) VALUES (?, ?, ?, ?)", (target_user_id, role_id, self.team_id, self.expires_on))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")

@save_to_command_log
@dataclass
class GrantSeriesRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    series_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if self.expires_on and self.expires_on < timestamp:
                raise Problem("Role cannot expire in the past", status=400)
            
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM series_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_series_roles WHERE user_id = ? AND role_id = ? AND series_id = ?", (target_user_id, role_id, self.series_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem(f"Player already has role {self.role}", status=400)
            
            # if we have the series_permissions.MANAGE_SERIES_ROLES global permission, bypass series role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.granter_user_id, series_permissions.MANAGE_SERIES_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to grant a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to grant, and has the MANAGE_SERIES_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM series_roles r1
                        JOIN user_series_roles ur ON ur.role_id = r1.id
                        JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN series_permissions p ON rp.permission_id = p.id
                        JOIN series_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.series_id = ?
                    )
                    """, (self.granter_user_id, self.role, series_permissions.MANAGE_SERIES_ROLES, self.series_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to grant role", status=401)

            try:
                await db.execute("INSERT INTO user_series_roles(user_id, role_id, series_id, expires_on) VALUES (?, ?, ?, ?)", (target_user_id, role_id, self.series_id, self.expires_on))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class GrantTournamentRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    tournament_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if self.expires_on and self.expires_on < timestamp:
                raise Problem("Role cannot expire in the past", status=400)
            
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM tournament_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_tournament_roles WHERE user_id = ? AND role_id = ? AND tournament_id = ?", (target_user_id, role_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem(f"Player already has role {self.role}", status=400)
            
            # if we have the tournament_permissions.MANAGE_TOURNAMENT_ROLES global permission, bypass series/tournament role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.granter_user_id, tournament_permissions.MANAGE_TOURNAMENT_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])
            
            if not is_mod:
                # if we have the tournament_permissions.MANAGE_TOURNAMENT_ROLES series permission, bypass tournament role checks
                async with db.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM user_series_roles ur
                        JOIN tournaments t ON ur.series_id = t.series_id
                        JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN series_permissions p ON rp.permission_id = p.id
                        WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0 AND t.id = ?
                    )
                    """, (self.granter_user_id, tournament_permissions.MANAGE_TOURNAMENT_ROLES, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to grant a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to grant, and has the MANAGE_TOURNAMENT_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM tournament_roles r1
                        JOIN user_tournament_roles ur ON ur.role_id = r1.id
                        JOIN tournament_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN tournament_permissions p ON rp.permission_id = p.id
                        JOIN tournament_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.tournament_id = ?
                    )
                    """, (self.granter_user_id, self.role, tournament_permissions.MANAGE_TOURNAMENT_ROLES, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to grant role", status=401)

            try:
                await db.execute("INSERT INTO user_tournament_roles(user_id, role_id, tournament_id, expires_on) VALUES (?, ?, ?, ?)", (target_user_id, role_id, self.tournament_id, self.expires_on))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class RemoveRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
                
            async with db.execute("SELECT user_id FROM user_roles WHERE user_id = ? AND role_id = ?", (target_user_id, role_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player does not have role {self.role}", status=400)
                
            # to have permission to remove a role, we should have a role which is both higher
            # in the role hierarchy than the role we wish to remove, and has the MANAGE_USER_ROLES
            # permission.
            async with db.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM roles r1
                    JOIN user_roles ur ON ur.role_id = r1.id
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.id
                    JOIN roles r2
                    WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                    AND rp.is_denied = 0 AND p.name = ?
                )
                """, (self.remover_user_id, self.role, permissions.MANAGE_USER_ROLES)) as cursor:
                row = await cursor.fetchone()
                can_remove = row is not None and bool(row[0])

            if not can_remove:
                raise Problem("Not authorized to remove role", status=401)
            
            try:
                await db.execute("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?", (target_user_id, role_id))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class RemoveTeamRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    team_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM team_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_team_roles WHERE user_id = ? AND role_id = ? AND team_id = ?", (target_user_id, role_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player does not have role {self.role}", status=400)
            
            # if we have the team_permissions.MANAGE_TEAM_ROLES global permission, bypass team role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.remover_user_id, team_permissions.MANAGE_TEAM_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to remove a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to remove, and has the MANAGE_TEAM_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM team_roles r1
                        JOIN user_team_roles ur ON ur.role_id = r1.id
                        JOIN team_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN team_permissions p ON rp.permission_id = p.id
                        JOIN team_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.team_id = ?
                    )
                    """, (self.remover_user_id, self.role, team_permissions.MANAGE_TEAM_ROLES, self.team_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to remove role", status=401)

            try:
                await db.execute("DELETE FROM user_team_roles WHERE user_id = ? AND role_id = ? AND team_id = ?", (target_user_id, role_id, self.team_id))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class RemoveSeriesRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    series_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM series_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_series_roles WHERE user_id = ? AND role_id = ? AND series_id = ?", (target_user_id, role_id, self.series_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player does not have role {self.role}", status=400)
            
            # if we have the series_permissions.MANAGE_SERIES_ROLES global permission, bypass team role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.remover_user_id, series_permissions.MANAGE_SERIES_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to remove a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to remove, and has the MANAGE_SERIES_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM series_roles r1
                        JOIN user_series_roles ur ON ur.role_id = r1.id
                        JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN series_permissions p ON rp.permission_id = p.id
                        JOIN series_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.series_id = ?
                    )
                    """, (self.remover_user_id, self.role, series_permissions.MANAGE_SERIES_ROLES, self.series_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to remove role", status=401)

            try:
                await db.execute("DELETE FROM user_series_roles WHERE user_id = ? AND role_id = ? AND series_id = ?", (target_user_id, role_id, self.series_id))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class RemoveTournamentRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    tournament_id: int
    role: str

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM tournament_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
            
            async with db.execute("SELECT user_id FROM user_tournament_roles WHERE user_id = ? AND role_id = ? AND tournament_id = ?", (target_user_id, role_id, self.tournament_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem(f"Player does not have role {self.role}", status=400)
            
            # if we have the tournament_permissions.MANAGE_TOURNAMENT_ROLES global permission, bypass team role checks
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0
                )
                """, (self.remover_user_id, tournament_permissions.MANAGE_TOURNAMENT_ROLES)) as cursor:
                row = await cursor.fetchone()
                is_mod = row is not None and bool(row[0])

            if not is_mod:
                # if we have the tournament_permissions.MANAGE_TOURNAMENT_ROLES series permission, bypass tournament role checks
                async with db.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM user_series_roles ur
                        JOIN tournaments t ON ur.series_id = t.series_id
                        JOIN series_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN series_permissions p ON rp.permission_id = p.id
                        WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 0 AND t.id = ?
                    )
                    """, (self.remover_user_id, tournament_permissions.MANAGE_TOURNAMENT_ROLES, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    is_mod = row is not None and bool(row[0])
        
            if not is_mod:
                # to have permission to remove a role, we should have a role which is both higher
                # in the role hierarchy than the role we wish to remove, and has the MANAGE_TOURNAMENT_ROLES
                # permission.
                async with db.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM tournament_roles r1
                        JOIN user_tournament_roles ur ON ur.role_id = r1.id
                        JOIN tournament_role_permissions rp ON ur.role_id = rp.role_id
                        JOIN tournament_permissions p ON rp.permission_id = p.id
                        JOIN tournament_roles r2
                        WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                        AND rp.is_denied = 0 AND p.name = ? AND ur.tournament_id = ?
                    )
                    """, (self.remover_user_id, self.role, tournament_permissions.MANAGE_TOURNAMENT_ROLES, self.tournament_id)) as cursor:
                    row = await cursor.fetchone()
                    can_grant = row is not None and bool(row[0])
                if not can_grant:
                    raise Problem("Not authorized to remove role", status=401)

            try:
                await db.execute("DELETE FROM user_tournament_roles WHERE user_id = ? AND role_id = ? AND tournament_id = ?", (target_user_id, role_id, self.tournament_id))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")
            
@save_to_command_log
@dataclass
class UpdateRoleExpirationCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if self.expires_on and self.expires_on < timestamp:
                raise Problem("Role cannot expire in the past", status=400)
            
            # get user id from player
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (self.target_player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                target_user_id = row[0]
            
            # get role id from name
            async with db.execute("SELECT id FROM roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
        
            # to have permission to grant a role, we should have a role which is both higher
            # in the role hierarchy than the role we wish to grant, and has the MANAGE_USER_ROLES
            # permission.
            async with db.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM roles r1
                    JOIN user_roles ur ON ur.role_id = r1.id
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p ON rp.permission_id = p.id
                    JOIN roles r2
                    WHERE ur.user_id = ? AND r2.name = ? AND r1.position < r2.position
                    AND rp.is_denied = 0 AND p.name = ?
                )
                """, (self.granter_user_id, self.role, permissions.MANAGE_USER_ROLES)) as cursor:
                row = await cursor.fetchone()
                can_grant = row is not None and bool(row[0])

            if not can_grant:
                raise Problem("Not authorized to grant role", status=401)

            try:
                await db.execute("UPDATE user_roles SET expires_on = ? WHERE user_id = ? AND role_id = ?", (self.expires_on, target_user_id, role_id))
                await db.commit()
            except Exception:
                raise Problem("Unexpected error")

@save_to_command_log
@dataclass
class RemoveExpiredRolesCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        timestamp = int(datetime.now(timezone.utc).timestamp())
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM user_roles WHERE expires_on < ?", (timestamp,))
            await db.execute("DELETE FROM user_team_roles WHERE expires_on < ?", (timestamp,))
            await db.execute("DELETE FROM user_series_roles WHERE expires_on < ?", (timestamp,))
            await db.execute("DELETE FROM user_tournament_roles WHERE expires_on < ?", (timestamp,))
            await db.commit()