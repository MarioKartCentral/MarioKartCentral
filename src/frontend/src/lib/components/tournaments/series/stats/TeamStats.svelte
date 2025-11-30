<!-- Main component -->
<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/table/Table.svelte';
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
    <Table data={rostersArray} let:item={roster}>
      <colgroup slot="colgroup">
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
      </colgroup>
      <tr slot="header">
        <th></th>
        <th></th>
        <th></th>
        {#if stats_mode === StatsMode.TEAM_MEDALS}
          <th class="text_center">👑</th><th class="text_center">🥈</th><th class="text_center">🥉</th>
        {:else}
          <th class="text_center bold">Appearances</th>
        {/if}
      </tr>

      {#if (stats_mode === StatsMode.TEAM_MEDALS && (roster.gold > 0 || roster.silver > 0 || roster.bronze > 0)) || (stats_mode === StatsMode.TEAM_APPEARANCES && roster.appearances_placement < 25)}
        <tr class="row">
          <td class="text_center bold {getColorClass(roster)}">
            {stats_mode === StatsMode.TEAM_MEDALS ? roster.medals_placement : roster.appearances_placement}
          </td>
          <td class={getColorClass(roster)}>
            <TagBadge tag={roster.roster_tag ? roster.roster_tag : roster.team_tag} color={roster.team_color} />
          </td>
          <td class={getColorClass(roster)}>
            <span class="white">
              <a href={`/${$page.params.lang}/registry/teams/profile?id=${roster.team_id}`}>
                {roster.roster_name ? roster.roster_name : roster.team_name}
              </a>
            </span>
          </td>
          {#if stats_mode === StatsMode.TEAM_MEDALS}
            <td class="text_center {getColorClass(roster)} {roster.gold > 0 ? 'bold' : ''}">
              {roster.gold > 0 ? roster.gold : '—'}
            </td>
            <td class="text_center {getColorClass(roster)} {roster.silver > 0 ? 'bold' : ''}">
              {roster.silver > 0 ? roster.silver : '—'}
            </td>
            <td class="text_center {getColorClass(roster)} {roster.bronze > 0 ? 'bold' : ''}">
              {roster.bronze > 0 ? roster.bronze : '—'}
            </td>
          {:else}
            <td class="text_center bold {getColorClass(roster)}">{roster.appearances}</td>
          {/if}
        </tr>
      {/if}
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
