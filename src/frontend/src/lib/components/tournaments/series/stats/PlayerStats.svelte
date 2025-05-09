<script lang="ts">
  import Flag from '$lib/components/common/Flag.svelte';
  import Table from '$lib/components/common/Table.svelte';

  export let stats_mode: 'player_medals' | 'player_appearances';
  export let playersArray: any[];
</script>

<Table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      {#if stats_mode === 'player_medals'}
        <th>👑</th><th>🥈</th><th>🥉</th>
      {:else}
        <th>Appearances</th>
      {/if}
    </tr>
  </thead>
  {#each playersArray as player}
    <tr>
      <td>{stats_mode === 'player_medals' ? player.medals_placement : player.appearances_placement}</td>
      <td><Flag country_code={player.country_code} size="small"/></td>
      <td>{player.name}</td>
      {#if stats_mode === 'player_medals'}
        <td>{player.gold > 0 ? player.gold : '-'}</td>
        <td>{player.silver > 0 ? player.silver : '-'}</td>
        <td>{player.bronze > 0 ? player.bronze : '-'}</td>
      {:else}
        <td>{player.appearances}</td>
      {/if}
    </tr>
  {/each}
</Table>
