from dataclasses import dataclass
from common.auth import roles
from common.data.commands import Command, save_to_command_log
from common.data.models import *
from common.auth.roles import BANNED
from datetime import datetime, timezone

@dataclass
class ListRolesCommand(Command[None]):
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
class GetRoleInfoCommand(Command[None]):
    role_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
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
            
            players: list[Player] = []
            async with db.execute(f"""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.discord_id
                FROM user_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ?
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.role_id, timestamp)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id = row
                    players.append(Player(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, discord_id))
            role_info = RoleInfo(self.role_id, role_name, position, permissions, players)
            return role_info

                
@dataclass
class GetUserRolePermissionsCommand(Command[tuple[list[Role], list[TeamRole], list[SeriesRole], list[TournamentRole]]]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            timestamp = int(datetime.now(timezone.utc).timestamp())
            
            # user roles
            role_dict: dict[int, UserRole] = {}
            async with db.execute("""
                SELECT DISTINCT r.id, r.name, r.position, ur.expires_on
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.user_id = ?
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
                AND (ur.expires_on > ? OR ur.expires_on IS NULL)
                """, (self.user_id, timestamp)) as cursor:
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
            
