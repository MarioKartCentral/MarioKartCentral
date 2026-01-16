from dataclasses import dataclass
from common.auth import team_permissions, permissions, team_roles
from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone
        
@dataclass
class ListTeamRolesCommand(Command[list[Role]]):
    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(readonly=True) as db:
            roles: list[Role] = []
            async with db.execute("SELECT id, name, position FROM team_roles") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    id, name, position = row
                    roles.append(Role(id, name, position))
            return roles

@dataclass
class GetTeamRoleInfoCommand(Command[TeamRoleInfo]):
    role_id: int
    team_id: int

    async def handle(self, db_wrapper: DBWrapper) -> TeamRoleInfo:
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("SELECT name, position FROM team_roles WHERE id = ?", (self.role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Role not found", status=400)
                role_name, position = row

            permissions: list[Permission] = []
            async with db.execute("""
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
            async with db.execute("""
                SELECT p.id, p.name, p.country_code, p.is_hidden, p.is_shadow, p.is_banned, p.is_verified, p.join_date, ur.expires_on
                FROM user_team_roles ur
                JOIN users u ON u.id = ur.user_id
                JOIN players p ON p.id = u.player_id
                WHERE ur.role_id = ?  AND ur.team_id = ?
                """, (self.role_id, self.team_id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, player_name, country_code, is_hidden, is_shadow, is_banned, is_verified, join_date, expires_on = row
                    players.append(RolePlayer(player_id, player_name, country_code, bool(is_hidden), bool(is_shadow), bool(is_banned), bool(is_verified), join_date, None, expires_on))
            role_info = TeamRoleInfo(self.role_id, role_name, position, permissions, players, self.team_id)
            return role_info

@dataclass
class GrantTeamRoleCommand(Command[None]):
    granter_user_id: int
    target_player_id: int
    team_id: int
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
            async with db.execute("SELECT id FROM team_roles where name = ?", (self.role,)) as cursor:
                row = await cursor.fetchone()
                role_id = None if row is None else int(row[0])

                if role_id is None:
                    raise Problem("Role not found", status=404)
                
            # check all the rosters the target player is in, if any of them already have 4 leaders then throw an error
            if self.role == team_roles.LEADER:
                async with db.execute("""SELECT MAX(roster_count)
                                      FROM (
                                        SELECT tr.id, COUNT(utr.user_id) AS roster_count
                                        FROM user_team_roles utr
                                        JOIN team_rosters tr ON tr.team_id = utr.team_id
                                        JOIN team_members tm ON tm.roster_id = tr.id
                                        JOIN users u ON u.player_id = tm.player_id
                                        WHERE utr.role_id = ? AND utr.team_id = ? AND tm.leave_date IS NULL 
                                        AND u.id = utr.user_id
                                        AND tm.roster_id IN (
                                            SELECT tm.roster_id
                                            FROM team_members tm
                                            WHERE tm.leave_date IS NULL AND tm.player_id = ?
                                        )
                                        GROUP BY tr.id
                                      )""", (role_id, self.team_id, self.target_player_id)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        count = row[0]
                        print(count)
                        if count is not None and count >= 4:
                            raise Problem("Team rosters can only have a maximum of 4 leaders", status=400)
            
            async with db.execute("SELECT user_id FROM user_team_roles WHERE user_id = ? AND role_id = ? AND team_id = ?", (target_user_id, role_id, self.team_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    raise Problem(f"Player already has role {self.role}", status=400)
                
            # if player has create teams permission denied, don't let someone else grant them a team role either
            async with db.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_roles ur
                    JOIN role_permissions rp ON ur.role_id = rp.role_id
                    JOIN permissions p On rp.permission_id = p.id
                    WHERE ur.user_id = ? AND p.name = ? AND rp.is_denied = 1
                )""", (target_user_id, permissions.CREATE_TEAM)) as cursor:
                row = await cursor.fetchone()
                denied_team_perm = row is not None and bool(row[0])
                if denied_team_perm:
                    raise Problem("Player is not allowed to lead teams", status=401)
            
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

@dataclass
class RemoveTeamRoleCommand(Command[None]):
    remover_user_id: int
    target_player_id: int
    team_id: int
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