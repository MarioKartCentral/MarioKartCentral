<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { sortByMedals, sortByAppearances } from '$lib/util/series_stats';
  export let stats;
  let stats_mode = 'medals';
  stats.rostersArray = sortByMedals(stats.rostersArray);

  function handleMedalsClick() {
    stats_mode = 'medals';
    stats.rostersArray = sortByMedals(stats.rostersArray);
  }

  function handleAppearancesClick() {
    stats_mode = 'appearances';
    stats.rostersArray = sortByAppearances(stats.rostersArray);
  }

</script>

<div>
    <button on:click={() => handleMedalsClick()}> Medals </button>
    <button on:click={() => handleAppearancesClick()}> Appearances </button>
    {#if stats_mode === 'medals'}
        <Table>
            <col class="placement" />
            <col class="team_tag" />
            <col class="team_name" />
            <col class="gold" />
            <col class="silver" />
            <col class="bronze" />
            <thead><tr><th></th><th></th><th></th><th>👑</th><th>🥈</th><th>🥉</th></tr></thead>
            {#each stats.rostersArray as roster}
            <tr>
                <td>{roster.medals_placement}</td>
                <td><TagBadge tag={roster.tag} color={1} /></td>
                <td>{roster.name}</td>
                <td>{roster.gold > 0 ? roster.gold : '-'}</td>
                <td>{roster.silver > 0 ? roster.silver : '-'}</td>
                <td>{roster.bronze > 0 ? roster.bronze : '-'}</td>
            </tr>
            {/each}
        </Table>
    {/if}
    {#if stats_mode === 'appearances'}
        <Table>
            <col class="placement" />
            <col class="team_tag" />
            <col class="team_name" />
            <col class="appearances" />
            <thead><tr><th></th><th></th><th></th><th>Appearances</th></tr></thead>
            {#each stats.rostersArray as roster}
            <tr>
                <td>{roster.appearances_placement}</td>
                <td><TagBadge tag={roster.tag} color={1} /></td>
                <td>{roster.name}</td>
                <td>{roster.appearances}</td>
            </tr>
            {/each}
        </Table>
    {/if}
</div>

<style></style>
