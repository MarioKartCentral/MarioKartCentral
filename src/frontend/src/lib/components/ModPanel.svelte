<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { permissions } from '$lib/util/util';
  import { page } from '$app/stores';
  import Dropdown from './common/Dropdown.svelte';
  import DropdownItem from './common/DropdownItem.svelte';
  import { NavLi } from 'flowbite-svelte';
  import { ChevronDownOutline } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';
  import AlertCount from './common/AlertCount.svelte';

  let user_info: UserInfo;
  let unread_count = 0;

  user.subscribe((value) => {
    user_info = value;
    let mod_notifs = value.mod_notifications
    if(mod_notifs) {
      unread_count = mod_notifs.pending_teams + mod_notifs.pending_team_edits + mod_notifs.pending_transfers;
    }
  });

  // underline a nav item if it's the section we're currently in
  function checkSelectedNav(name: string) {
    if($page.data.activeNavItem === name) {
      return "text-white font-bold underline underline-offset-4";
    }
    return "";
  }
</script>

<NavLi class="cursor-pointer {checkSelectedNav("MODERATOR")}">
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