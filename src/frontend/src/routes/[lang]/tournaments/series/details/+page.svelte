<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import SeriesInfo from '$lib/components/tournaments/series/SeriesInfo.svelte';
  import SeriesStats from '$lib/components/tournaments/series/SeriesStats.svelte';
  import SeriesPosts from '$lib/components/tournaments/series/SeriesPosts.svelte';
  import SeriesPodiums from '$lib/components/tournaments/series/SeriesPodiums.svelte';
  import type { TournamentWithPlacements } from '$lib/types/tournament';
  import type { CombinedSeriesStats } from '$lib/types/series-stats';

  import LL from '$i18n/i18n-svelte';
  import { makeStats } from '$lib/util/series_stats';

  let id = 0;
  let series: TournamentSeries;
  let stats: CombinedSeriesStats;
  let tournaments: TournamentWithPlacements[];
  let not_found = false;
  $: series_name = series ? series.series_name : 'Tournament Series';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const resSeries = await fetch(`/api/tournaments/series/${id}`);
    if (resSeries.status !== 200) {
      not_found = true;
      return;
    }
    const series_body: TournamentSeries = await resSeries.json();
    series = series_body;

    const resSeriesPl = await fetch(`/api/tournaments/series/${id}/placements`);
    if (resSeriesPl.status !== 200) {
      not_found = true;
      return;
    }
    const tournaments_body: TournamentWithPlacements[] = await resSeriesPl.json();
    tournaments = tournaments_body;
    stats = makeStats(tournaments);
  });
</script>

<svelte:head>
  <title>{series_name} | MKCentral</title>
</svelte:head>

{#if series}
  <SeriesInfo {series} />
  <SeriesPosts {series} />
  {#if tournaments}
    <SeriesPodiums {tournaments} />
    <SeriesStats {stats} />
  {/if}
{:else if not_found}
  {$LL.TOURNAMENTS.SERIES.NOT_FOUND()}
{/if}
