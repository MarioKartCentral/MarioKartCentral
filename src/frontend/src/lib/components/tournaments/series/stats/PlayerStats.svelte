<script lang="ts">
  import Flag from '$lib/components/common/Flag.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { StatsMode } from '$lib/types/tournament';

  export let stats_mode: StatsMode;
  export let playersArray: any[];

  function getColorClass(roster) {
    if (stats_mode === 'player_medals') {
      if (roster.medals_placement === 1) {
        return 'gold_row';
      }
      if (roster.medals_placement === 2) {
        return 'silver_row';
      }
      if (roster.medals_placement === 3) {
        return 'bronze_row';
      }
    } else {
      if (roster.appearances_placement === 1) {
        return 'gold_row';
      }
      if (roster.appearances_placement === 2) {
        return 'silver_row';
      }
      if (roster.appearances_placement === 3) {
        return 'bronze_row';
      }
      return '';
    }
  }
</script>

<Table>
  <col class="placement" />
  <col class="tag" />
  <col class="name" />
  {#if stats_mode === StatsMode.PLAYER_MEDALS}
    <col class="medals" />
    <col class="medals" />
    <col class="medals" />
  {:else}
    <col class="appearances" />
  {/if}
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      {#if stats_mode === StatsMode.PLAYER_MEDALS}
        <th class="text_center">👑</th><th class="text_center">🥈</th><th class="text_center">🥉</th>
      {:else}
        <th class="bold_td text_center">Appearances</th>
      {/if}
    </tr>
  </thead>
  {#each playersArray as player}
    {#if (stats_mode === StatsMode.PLAYER_MEDALS && (player.gold > 0 || player.silver > 0 || player.bronze > 0)) || (stats_mode === StatsMode.PLAYER_APPEARANCES && player.appearances_placement < 25)}
      <tr class={getColorClass(player)}>
        <td class="text_center bold_td"
          >{stats_mode === StatsMode.PLAYER_MEDALS ? player.medals_placement : player.appearances_placement}</td
        >
        <td><Flag country_code={player.country_code} size="small" /></td>
        <td>{player.name}</td>
        {#if stats_mode === StatsMode.PLAYER_MEDALS}
          <td class="text_center bold_td">{player.gold > 0 ? player.gold : '-'}</td>
          <td class="text_center bold_td">{player.silver > 0 ? player.silver : '-'}</td>
          <td class="text_center bold_td">{player.bronze > 0 ? player.bronze : '-'}</td>
        {:else}
          <td class="text_center bold_td">{player.appearances}</td>
        {/if}
      </tr>
    {/if}
  {/each}
</Table>

<style>
  .table-container {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .compact-table {
    width: fit-content;
    table-layout: fixed;
    border-collapse: collapse;
  }

  col.placement {
    width: 64px;
  }
  col.tag {
    width: 64px;
  }
  col.name {
    width: 256px;
  }
  col.medals {
    width: 64px;
  }

  col.appearances {
    width: 192px;
  }

  .text_center {
    text-align: center;
  }

  .gold_row {
    color: #fffab0;
    background-color: rgba(255, 253, 108, 0.25);
  }

  .silver_row {
    color: #dddddd;
    background-color: rgba(195, 255, 255, 0.25);
  }

  .bronze_row {
    color: #ffcbae;
    background-color: rgba(255, 158, 110, 0.25);
  }

  .bold_td {
    font-weight: bold;
  }
</style>
