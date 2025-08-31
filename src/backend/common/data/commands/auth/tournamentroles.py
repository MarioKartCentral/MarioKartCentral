from dataclasses import dataclass
from common.auth import tournament_permissions
from common.data.commands import Command, save_to_command_log
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *
from datetime import datetime, timezone


@dataclass
class ListTournamentRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            async with db.execute("SELECT id, name, position FROM tournament_roles") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles

@dataclass
class GetTournamentRoleInfoCommand(Command[TournamentRoleInfo]):
    role_id: int
    tournament_id: int

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM tournament_roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute("""
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
            async with db.execute("""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.join_date, ur.expires_on
                FROM user_tournament_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ? AND ur.tournament_id = ?
                """, (self.role_id, self.tournament_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, join_date, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, is_hidden, is_shadow, is_banned, join_date, None, expires_on))
            role_info = TournamentRoleInfo(self.role_id, role_name, position, permissions, players, self.tournament_id)
            return role_info
            
@save_to_command_log
@dataclass
class GrantTournamentRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    tournament_id: int
    role: str
    expires_on: int | None = None

    async def handle(self, db_wrapper: DBWrapper) -> None:
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
class RemoveTournamentRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    tournament_id: int
    role: str

    async def handle(self, db_wrapper: DBWrapper) -> None:
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