<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TeamStats from '$lib/components/tournaments/series/stats/TeamStats.svelte';
  import PlayerStats from '$lib/components/tournaments/series/stats/PlayerStats.svelte';
  import { compareMedals } from '$lib/util/series_stats';
  import { StatsMode } from '$lib/types/tournament';
  import type { CombinedSeriesStats } from '$lib/types/series-stats';
  import LL from '$i18n/i18n-svelte';

  export let stats: CombinedSeriesStats;

  let stats_mode: StatsMode = stats.roster_stats.length > 0 ? StatsMode.TEAM_MEDALS : StatsMode.PLAYER_MEDALS;

  $: sortedRosters =
    stats_mode === StatsMode.TEAM_MEDALS
      ? stats.roster_stats.sort(compareMedals)
      : stats.roster_stats.sort((a, b) => b.appearances - a.appearances);

  $: sortedPlayers =
    stats_mode === StatsMode.PLAYER_MEDALS
      ? stats.player_stats.sort(compareMedals)
      : stats.player_stats.sort((a, b) => b.appearances - a.appearances);
</script>

<Section header={$LL.TOURNAMENTS.SERIES.STATS()}>
  {#if stats_mode === StatsMode.TEAM_MEDALS || stats_mode === StatsMode.TEAM_APPEARANCES}
    <div class="stats_container">
      <Button on:click={() => (stats_mode = StatsMode.TEAM_MEDALS)}>Podium Finishes</Button>
      <Button on:click={() => (stats_mode = StatsMode.TEAM_APPEARANCES)}>Tournament Appearances</Button>
    </div>
    <TeamStats {stats_mode} rostersArray={sortedRosters} />
  {:else}
    <div class="stats_container">
      <Button on:click={() => (stats_mode = StatsMode.PLAYER_MEDALS)}>Podium Finishes</Button>
      <Button on:click={() => (stats_mode = StatsMode.PLAYER_APPEARANCES)}>Tournament Appearances</Button>
    </div>
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
