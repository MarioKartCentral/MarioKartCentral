<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import Table from '$lib/components/common/Table.svelte';

  export let tournament: Tournament;
  export let players: TournamentPlayer[];
</script>

<Table>
  <col class="country" />
  <col class="name" />
  {#if tournament.mii_name_required}
    <col class="mii-name" />
  {/if}
  <col class="friend-codes" />
  {#if tournament.host_status_required}
    <col class="can-host" />
  {/if}
  <thead>
    <tr>
      <th />
      <th>Name</th>
      {#if tournament.mii_name_required}
        <th>In-Game Name</th>
      {/if}
      <th>Friend Codes</th>
      {#if tournament.host_status_required}
        <th>Can Host</th>
      {/if}
    </tr>
  </thead>
  <tbody>
    {#each players as player, i}
      <tr class="row-{i % 2}">
        <td>{player.country_code}</td>
        <td>{player.name}</td>
        {#if tournament.mii_name_required}
          <td>{player.mii_name}</td>
        {/if}
        <td>
          {#if player.friend_codes.length > 0}
            {player.friend_codes[0]}
          {/if}
        </td>
        {#if tournament.host_status_required}
          <td>{player.can_host ? 'Yes' : 'No'}</td>
        {/if}
      </tr>
    {/each}
  </tbody>
</Table>

<style>
  col.country {
    width: 5%;
  }
  col.name {
    width: 30%;
  }
  col.mii-name {
    width: 30%;
  }
  col.friend-codes {
    width: 25%;
  }
  col.can-host {
    width: 10%;
  }
</style>
