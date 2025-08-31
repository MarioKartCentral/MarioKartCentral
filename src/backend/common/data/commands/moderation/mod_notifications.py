from dataclasses import dataclass
from common.auth import permissions
from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper
from common.data.models import *

@dataclass
class GetModNotificationsCommand(Command[ModNotifications]):
    user_roles: list[UserRole]

    async def handle(self, db_wrapper: DBWrapper):
        mod_notifications = ModNotifications()
        string_perms: list[str] = []
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
                async with db.execute("SELECT COUNT(id) FROM team_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
                async with db.execute("SELECT COUNT(id) FROM roster_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_team_edits += row[0]
            if permissions.MANAGE_TRANSFERS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM team_transfers WHERE is_accepted = 1 AND approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_transfers = row[0]
            if permissions.EDIT_PLAYER in string_perms:
                async with db.execute("SELECT COUNT(id) FROM player_name_edits WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_player_name_changes = row[0]
            if permissions.MANAGE_SHADOW_PLAYERS in string_perms:
                async with db.execute("SELECT COUNT(id) FROM player_claims WHERE approval_status='pending'") as cursor:
                    row = await cursor.fetchone()
                    assert row is not None
                    mod_notifications.pending_player_claims = row[0]
        return mod_notifications
    
