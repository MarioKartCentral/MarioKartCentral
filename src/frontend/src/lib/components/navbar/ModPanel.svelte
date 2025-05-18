<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { page } from '$app/stores';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import LL from '$i18n/i18n-svelte';
  import AlertCount from '$lib/components/common/AlertCount.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });
</script>

<Dropdown>
  {#if check_permission(user_info, permissions.manage_teams)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_teams">
      {$LL.NAVBAR.MOD_PANEL.APPROVE_TEAMS()}
      {#if user_info.mod_notifications?.pending_teams}
        <AlertCount count={user_info.mod_notifications.pending_teams}/>
      {/if}
      
    </DropdownItem>
    <DropdownItem href="/{$page.params.lang}/moderator/approve_team_edits">
      {$LL.NAVBAR.MOD_PANEL.TEAM_NAME_TAG_CHANGES()}
      {#if user_info.mod_notifications?.pending_team_edits}
        <AlertCount count={user_info.mod_notifications.pending_team_edits}/>
      {/if}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.manage_transfers)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_transfers">
      {$LL.NAVBAR.MOD_PANEL.APPROVE_TRANSFERS()}
      {#if user_info.mod_notifications?.pending_transfers}
        <AlertCount count={user_info.mod_notifications.pending_transfers}/>
      {/if}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.manage_user_roles)}
    <DropdownItem href="/{$page.params.lang}/moderator/manage_user_roles">
      {$LL.NAVBAR.MOD_PANEL.USER_ROLES()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.ban_player)}
    <DropdownItem href="/{$page.params.lang}/moderator/player_bans">
      {$LL.NAVBAR.MOD_PANEL.PLAYER_BANS()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.edit_player)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_player_names">
      {$LL.NAVBAR.MOD_PANEL.PLAYER_NAME_CHANGES()}
      {#if user_info.mod_notifications?.pending_player_name_changes}
        <AlertCount count={user_info.mod_notifications.pending_player_name_changes}/>
      {/if}
    </DropdownItem>
    <DropdownItem href="/{$page.params.lang}/moderator/friend_code_edits">
      {$LL.NAVBAR.MOD_PANEL.FRIEND_CODE_CHANGES()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.manage_shadow_players)}
    <DropdownItem href="/{$page.params.lang}/moderator/shadow_players">
      {$LL.NAVBAR.MOD_PANEL.SHADOW_PLAYERS()}
    </DropdownItem>
    <DropdownItem href="/{$page.params.lang}/moderator/player_claims">
      {$LL.NAVBAR.MOD_PANEL.PLAYER_CLAIMS()}
      {#if user_info.mod_notifications?.pending_player_claims}
        <AlertCount count={user_info.mod_notifications.pending_player_claims}/>
      {/if}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.merge_players)}
    <DropdownItem href="/{$page.params.lang}/moderator/merge_players">
      {$LL.NAVBAR.MOD_PANEL.MERGE_PLAYERS()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.merge_teams)}
    <DropdownItem href="/{$page.params.lang}/moderator/merge_teams">
      {$LL.NAVBAR.MOD_PANEL.MERGE_TEAMS()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.manage_word_filter)}
    <DropdownItem href="/{$page.params.lang}/moderator/word_filter">
      {$LL.NAVBAR.MOD_PANEL.WORD_FILTER()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.edit_user)}
    <DropdownItem href="/{$page.params.lang}/moderator/users">
      {$LL.NAVBAR.MOD_PANEL.MANAGE_USERS()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.view_alt_flags)}
    <DropdownItem href="/{$page.params.lang}/moderator/alt_detection">
      {$LL.NAVBAR.MOD_PANEL.ALT_DETECTION()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.view_fingerprints)}
    <DropdownItem href="/{$page.params.lang}/moderator/fingerprints">
        {$LL.NAVBAR.MOD_PANEL.FINGERPRINTS()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.view_basic_ip_info)}
    <DropdownItem href="/{$page.params.lang}/moderator/ip_search">
        {$LL.NAVBAR.MOD_PANEL.IP_SEARCH()}
    </DropdownItem>
  {/if}
  {#if check_permission(user_info, permissions.create_db_backups)}
    <DropdownItem href="/{$page.params.lang}/admin/backup_db">
        Backup Database
    </DropdownItem>
  {/if}
</Dropdown>