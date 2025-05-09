<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TeamStats from '$lib/components/tournaments/series/stats/TeamStats.svelte';
  import PlayerStats from '$lib/components/tournaments/series/stats/PlayerStats.svelte';
  import { sortByMedals, sortByAppearances } from '$lib/util/series_stats';

  export let stats;

  enum StatsMode {
    TEAM_MEDALS = 'team_medals',
    TEAM_APPEARANCES = 'team_appearances',
    PLAYER_MEDALS = 'player_medals',
    PLAYER_APPEARANCES = 'player_appearances',
  }

  let stats_mode: StatsMode = StatsMode.TEAM_MEDALS;

  $: sortedRosters =
    stats_mode === StatsMode.TEAM_MEDALS ? sortByMedals(stats.rostersArray) : sortByAppearances(stats.rostersArray);

  $: sortedPlayers =
    stats_mode === StatsMode.PLAYER_MEDALS ? sortByMedals(stats.playersArray) : sortByAppearances(stats.playersArray);
</script>

<Section header="Stats">
  <div class="stats_container">
    {#if stats.rostersArray.length > 0}
      <Button on:click={() => (stats_mode = StatsMode.TEAM_MEDALS)}>Podium Finishes</Button>
      <Button on:click={() => (stats_mode = StatsMode.TEAM_APPEARANCES)}>Tournament Appearances</Button>
    {:else}
      <Button on:click={() => (stats_mode = StatsMode.PLAYER_MEDALS)}>Podium Finishes</Button>
      <Button on:click={() => (stats_mode = StatsMode.PLAYER_APPEARANCES)}>Tournament Appearances</Button>
    {/if}
  </div>
  {#if stats_mode === StatsMode.TEAM_MEDALS || stats_mode === StatsMode.TEAM_APPEARANCES}
    <TeamStats {stats_mode} rostersArray={sortedRosters} />
  {:else if stats_mode === StatsMode.PLAYER_MEDALS || stats_mode === StatsMode.PLAYER_APPEARANCES}
    <PlayerStats {stats_mode} playersArray={sortedPlayers} />
  {/if}
</Section>

<style>
  .stats_container {
    display: flex;
    justify-content: center;
    gap: 20px;
  }
</style>
