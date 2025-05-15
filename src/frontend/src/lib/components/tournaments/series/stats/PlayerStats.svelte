<script lang="ts">
  import Flag from '$lib/components/common/Flag.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { StatsMode } from '$lib/types/tournament';
  import { page } from '$app/stores';

  export let stats_mode: StatsMode;
  export let playersArray;

  function getColorClass(p) {
    if (stats_mode === 'player_medals') {
      if (p.medals_placement === 1) {
        return 'gold_row';
      }
      if (p.medals_placement === 2) {
        return 'silver_row';
      }
      if (p.medals_placement === 3) {
        return 'bronze_row';
      }
    } else {
      if (p.appearances_placement === 1) {
        return 'gold_row';
      }
      if (p.appearances_placement === 2) {
        return 'silver_row';
      }
      if (p.appearances_placement === 3) {
        return 'bronze_row';
      }
      return '';
    }
  }
</script>

{#if stats_mode === StatsMode.PLAYER_APPEARANCES}
  <h2 class="text_center bold top25">Showing Top 25</h2>
{/if}
<div class="table-container">
  <div class="compact-table">
    <Table>
      <col class="placement" />
      <col class="flag" />
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
            <th class="bold text_center">Appearances</th>
          {/if}
        </tr>
      </thead>
      {#each playersArray as p, i}
        {#if (stats_mode === StatsMode.PLAYER_MEDALS && (p.gold > 0 || p.silver > 0 || p.bronze > 0)) || (stats_mode === StatsMode.PLAYER_APPEARANCES && p.appearances_placement < 25)}
          <tr class="row-{i % 2}">
            <td class={'text_center bold ' + getColorClass(p)}>
              {stats_mode === StatsMode.PLAYER_MEDALS ? p.medals_placement : p.appearances_placement}
            </td>
            <td class={'text_center bold ' + getColorClass(p)}>
              <Flag country_code={p.country_code} size="small" />
            </td>
            <td class={getColorClass(p)}>
              <span class="white">
                <a href={`/${$page.params.lang}/registry/players/profile?id=${p.player_id}`}>
                  {p.name}
                </a>
              </span>
            </td>
            {#if stats_mode === StatsMode.PLAYER_MEDALS}
              <td class="text_center bold {getColorClass(p)}">{p.gold > 0 ? p.gold : '—'}</td>
              <td class="text_center bold {getColorClass(p)}">{p.silver > 0 ? p.silver : '—'}</td>
              <td class="text_center bold {getColorClass(p)}">{p.bronze > 0 ? p.bronze : '—'}</td>
            {:else}
              <td class="text_center bold {getColorClass(p)}">{p.appearances}</td>
            {/if}
          </tr>
        {/if}
      {/each}
    </Table>
  </div>
</div>

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
  col.flag {
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
    background-color: rgba(235, 255, 255, 0.2);
  }

  .bronze_row {
    color: #ffcbae;
    background-color: rgba(255, 158, 110, 0.25);
  }

  .bold {
    font-weight: bold;
  }

  .white {
    color: white;
  }

  .top25 {
    margin-top: 10px;
  }
</style>
