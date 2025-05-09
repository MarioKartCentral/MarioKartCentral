<!-- Main component -->
<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/Table.svelte';

  export let stats_mode: 'team_medals' | 'team_appearances';
  export let rostersArray: any[];

  function getColorClass(roster) {
    if(stats_mode === 'team_medals') {
      if(roster.medals_placement === 1) {
        return 'gold_row';
      }
      if(roster.medals_placement === 2) {
        return 'silver_row';
      }
      if(roster.medals_placement === 3) {
        return 'bronze_row'
      }
    } else {
      if(roster.appearances_placement === 1) {
        return 'gold_row';
      }
      if(roster.appearances_placement === 2) {
        return 'silver_row';
      }
      if(roster.appearances_placement === 3) {
        return 'bronze_row'
      }
      return '';
    }
  }
</script>

<div class="table-container">
  <div class="compact-table">
    <Table>
      <col class="placement" />
      <col class="tag" />
      <col class="name" />
      {#if stats_mode === 'team_medals'}
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
          {#if stats_mode === 'team_medals'}
            <th>👑</th><th>🥈</th><th>🥉</th>
          {:else}
            <th class="appearance bold_td">Appearances</th>
          {/if}
        </tr>
      </thead>
      {#each rostersArray as roster}
        {#if (stats_mode === 'team_medals' && (roster.gold > 0 || roster.silver > 0 || roster.bronze > 0)) || (stats_mode === 'team_appearances' && roster.appearances_placement < 25)}
          <tr class={getColorClass(roster)}>
            <td>{stats_mode === 'team_medals' ? roster.medals_placement : roster.appearances_placement}</td>
            <td><TagBadge tag={roster.tag} color={roster.color} /></td>
            <td>{roster.name}</td>
            {#if stats_mode === 'team_medals'}
              <td class="bold_td">{roster.gold > 0 ? roster.gold : '-'}</td>
              <td class="bold_td">{roster.silver > 0 ? roster.silver : '-'}</td>
              <td class="bold_td">{roster.bronze > 0 ? roster.bronze : '-'}</td>
            {:else}
              <td class="appearance bold_td">{roster.appearances}</td>
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

  .appearance {
    text-align: center;
  }

  .gold_row {
    color: #fffab0;
    background-color: rgba(255,253,108,.25);
  }

  .silver_row {
    color: #dddddd;
    background-color: rgba(195,255,255,.25);
  }

  .bronze_row {
    color: #ffcbae;
    background-color: rgba(255,158,110,.25);
  }

  .bold_td {
    font-weight: bold;
  }
</style>
