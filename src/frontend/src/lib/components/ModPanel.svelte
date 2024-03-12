<script lang="ts">
  import DropdownMenu from './DropdownMenu.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { permissions } from '$lib/util/util';
  import { page } from '$app/stores';
  import { Dropdown, DropdownItem } from 'flowbite-svelte';

  // let dropdown: DropdownMenu;
  // export function toggleModPanel() {
  //   dropdown.toggleDropdown();
  // }

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });
</script>
<Dropdown class="w-44 z-20 bg-green-600 text-white">
  {#if user_info.permissions.includes(permissions.manage_teams)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_teams" class="hover:text-black">
      Approve Teams {user_info.mod_notifications?.pending_teams
        ? `(${user_info.mod_notifications.pending_teams})`
        : ''}
    </DropdownItem>
    <DropdownItem href="/{$page.params.lang}/moderator/approve_team_edits" class="hover:text-black">
      Team Name/Tag Changes {user_info.mod_notifications?.pending_team_edits
        ? `(${user_info.mod_notifications.pending_team_edits})`
        : ''}
    </DropdownItem>
  {/if}
  {#if user_info.permissions.includes(permissions.manage_transfers)}
    <DropdownItem href="/{$page.params.lang}/moderator/approve_transfers" class="hover:text-black">
      Transfers {user_info.mod_notifications?.pending_transfers
        ? `(${user_info.mod_notifications.pending_transfers})`
        : ''}
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
