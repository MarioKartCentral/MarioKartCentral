<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import Flag from '$lib/components/common/Flag.svelte';
  import FriendCodeDisplay from '$lib/components/common/FriendCodeDisplay.svelte';
  export let players: PlayerInfo[];
</script>

<Table>
  <col class="country_code" />
  <col class="name" />
  <col class="friend_codes mobile-hide"/>
  <thead>
    <tr>
      <th></th>
      <th>{$LL.PLAYER_LIST.HEADER.NAME()}</th>
      <th class="mobile-hide">Friend Codes</th>
    </tr>
  </thead>
  <tbody>
    {#each players as player, i}
      <tr class="row-{i % 2}">
        <td><Flag country_code={player.country_code} /></td>
        <td>
          <a href="/{$page.params.lang}/registry/players/profile?id={player.id}" class={player.is_banned ? 'banned_name' : ''}>{player.name}</a>
        </td>
        <td class="mobile-hide">
          <FriendCodeDisplay friend_codes={player.friend_codes}/>
        </td>
      </tr>
    {/each}
  </tbody>
</Table>

<style>
  col.country_code {
    width: 20%;
  }
  col.name {
    width: 40%;
  }
  col.friend_codes {
    width: 40%;
  }
  .banned_name {
    opacity: 0.7;
    text-decoration: line-through;
  }
</style>
