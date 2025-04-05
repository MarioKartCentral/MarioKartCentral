<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import SeriesInfo from '$lib/components/tournaments/series/SeriesInfo.svelte';
  import LL from '$i18n/i18n-svelte';
  import SeriesPosts from '$lib/components/tournaments/series/SeriesPosts.svelte';
  import { makeStats } from '$lib/util/series_stats';
  import SeriesStats from '$lib/components/tournaments/series/SeriesStats.svelte';

  let id = 0;
  let series: TournamentSeries;
  let stats;
  let not_found = false;
  $: series_name = series ? series.series_name : 'Tournament Series';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/tournaments/series/${id}`);
    if (res.status !== 200) {
      not_found = true;
      return;
    }
    const res2 = await fetch(`/api/tournaments/series/${id}/placements`);
    if (res2.status !== 200) {
      not_found = true;
      return;
    }
    const body: TournamentSeries = await res.json();
    const body2: TournamentSeries = await res2.json();
    series = body;
    const tournaments = body2;
    console.log(tournaments);

    // const originalArray = series
    // const scaleFactor = 1_000_000_0;
    // const bigArray = Array.from({ length: originalArray.length * scaleFactor }, (_, i) => 
    //   originalArray[i % originalArray.length]
    // );
    // console.log(bigArray.length);
    stats = makeStats(tournaments);
    console.log(stats);
  });
</script>

<svelte:head>
  <title>{series_name} | Mario Kart Central</title>
</svelte:head>

{#if series}
  <SeriesInfo {series} />
  <SeriesPosts {series}/>
  <SeriesStats {stats} />
{:else if not_found}
  {$LL.TOURNAMENTS.SERIES.NOT_FOUND()}
{/if}
