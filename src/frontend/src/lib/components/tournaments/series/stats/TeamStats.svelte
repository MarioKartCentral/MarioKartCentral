<!-- Main component -->
<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { StatsMode } from '$lib/types/tournament';
  import { page } from '$app/stores';
  import type { RosterSeriesStats } from '$lib/types/series-stats';

  export let stats_mode: StatsMode;
  export let rostersArray: RosterSeriesStats[];

  function getColorClass(roster: RosterSeriesStats) {
    if (stats_mode === StatsMode.TEAM_MEDALS) {
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

{#if stats_mode === StatsMode.TEAM_APPEARANCES}
  <h2 class="text_center bold top25">Showing Top 25</h2>
{/if}
<div class="table-container">
  <div class="compact-table">
    <Table>
      <col class="placement" />
      <col class="tag" />
      <col class="name" />
      {#if stats_mode === StatsMode.TEAM_MEDALS}
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
          {#if stats_mode === StatsMode.TEAM_MEDALS}
            <th class="text_center">👑</th><th class="text_center">🥈</th><th class="text_center">🥉</th>
          {:else}
            <th class="text_center bold">Appearances</th>
          {/if}
        </tr>
      </thead>
      {#each rostersArray as r, i}
        {#if (stats_mode === StatsMode.TEAM_MEDALS && (r.gold > 0 || r.silver > 0 || r.bronze > 0)) || (stats_mode === StatsMode.TEAM_APPEARANCES && r.appearances_placement < 25)}
          <tr class="row-{i % 2}">
            <td class="text_center bold {getColorClass(r)}"
              >{stats_mode === StatsMode.TEAM_MEDALS ? r.medals_placement : r.appearances_placement}</td
            >
            <td class={getColorClass(r)}
              ><TagBadge tag={r.roster_tag ? r.roster_tag : r.team_tag} color={r.team_color} /></td
            >
            <td class={getColorClass(r)}>
              <span class="white">
                <a href={`/${$page.params.lang}/registry/teams/profile?id=${r.team_id}`}>
                  {r.roster_name ? r.roster_name : r.team_name}
                </a>
              </span>
            </td>
            {#if stats_mode === StatsMode.TEAM_MEDALS}
              <td class="text_center {getColorClass(r)} {r.gold > 0 ? 'bold' : ''}">{r.gold > 0 ? r.gold : '—'}</td>
              <td class="text_center {getColorClass(r)} {r.silver > 0 ? 'bold' : ''}"
                >{r.silver > 0 ? r.silver : '—'}</td
              >
              <td class="text_center {getColorClass(r)} {r.bronze > 0 ? 'bold' : ''}"
                >{r.bronze > 0 ? r.bronze : '—'}</td
              >
            {:else}
              <td class="text_center bold {getColorClass(r)}">{r.appearances}</td>
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
