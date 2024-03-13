<script lang="ts">
  import DropdownMenu from './DropdownMenu.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { permissions } from '$lib/util/util';
  import { page } from '$app/stores';
  // import { Dropdown, DropdownItem } from 'flowbite-svelte';
  import Dropdown from './common/Dropdown.svelte';
  import DropdownItem from './common/DropdownItem.svelte';
  import { NavLi } from 'flowbite-svelte';
  import { ChevronDownOutline } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';
  import AlertCount from './common/AlertCount.svelte';

  // let dropdown: DropdownMenu;
  // export function toggleModPanel() {
  //   dropdown.toggleDropdown();
  // }

  let user_info: UserInfo;
  let unread_count = 0;

  user.subscribe((value) => {
    user_info = value;
    let mod_notifs = value.mod_notifications
    if(mod_notifs) {
      unread_count = mod_notifs.pending_teams + mod_notifs.pending_team_edits + mod_notifs.pending_transfers;
    }
  });
</script>

<NavLi class="cursor-pointer">
  {$LL.NAVBAR.MODERATOR()}
  {#if unread_count}
    <AlertCount count={unread_count}/>
  {/if}
  <ChevronDownOutline class="inline"/>
  
</NavLi>
<Dropdown>
  {#if user_info.permissions.includes(permissions.manage_teams)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_teams">
      Approve Teams 
      {#if user_info.mod_notifications?.pending_teams}
        <AlertCount count={user_info.mod_notifications.pending_teams}/>
      {/if}
      
    </DropdownItem>
    <DropdownItem href="/{$page.params.lang}/moderator/approve_team_edits">
      Team Name/Tag Changes
      {#if user_info.mod_notifications?.pending_team_edits}
        <AlertCount count={user_info.mod_notifications.pending_team_edits}/>
      {/if}
    </DropdownItem>
  {/if}
  {#if user_info.permissions.includes(permissions.manage_transfers)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_transfers">
      Transfers
      {#if user_info.mod_notifications?.pending_transfers}
        <AlertCount count={user_info.mod_notifications.pending_transfers}/>
      {/if}
    </DropdownItem>
  {/if}
</Dropdown>

<!-- <DropdownMenu bind:this={dropdown}>
  {#if user_info.permissions.includes(permissions.manage_teams)}
    <div>
      <a href="/{$page.params.lang}/moderator/approve_teams"
        >Approve Teams {user_info.mod_notifications?.pending_teams
          ? `(${user_info.mod_notifications.pending_teams})`
          : ''}</a
      >
    </div>
    <div>
      <a href="/{$page.params.lang}/moderator/approve_team_edits"
        >Team Name/Tag Changes {user_info.mod_notifications?.pending_team_edits
          ? `(${user_info.mod_notifications.pending_team_edits})`
          : ''}</a
      >
    </div>
  {/if}
  {#if user_info.permissions.includes(permissions.manage_transfers)}
    <div>
      <a href="/{$page.params.lang}/moderator/approve_transfers"
        >Transfers {user_info.mod_notifications?.pending_transfers
          ? `(${user_info.mod_notifications.pending_transfers})`
          : ''}</a
      >
    </div>
  {/if}
</DropdownMenu> -->
