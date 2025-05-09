<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import SeriesInfo from '$lib/components/tournaments/series/SeriesInfo.svelte';
  import SeriesStats from '$lib/components/tournaments/series/SeriesStats.svelte';
  import SeriesPosts from '$lib/components/tournaments/series/SeriesPosts.svelte';
  import SeriesPodiums from '$lib/components/tournaments/series/SeriesPodiums.svelte';

  import LL from '$i18n/i18n-svelte';
  import { makeStats } from '$lib/util/series_stats';

  let id = 0;
  let series: TournamentSeries;
  let stats;
  let tournaments;
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
    const resSeriesPl = await fetch(`/api/tournaments/series/${id}/placements`);
    if (resSeriesPl.status !== 200) {
      not_found = true;
      return;
    }
    const body1: TournamentSeries = await resSeries.json();
    const body2: TournamentSeries = await resSeriesPl.json();
    console.log(body1)
    series = body1;
    tournaments = body2;
    console.log("tournaments : ", tournaments);

    // const originalArray = body2
    // const scaleFactor = 50_000_000;
    // const bigArray = Array.from({ length: originalArray.length * scaleFactor }, (_, i) => 
    //   originalArray[i % originalArray.length]
    // );
    // console.log(bigArray.length);

    stats = makeStats(body2);
    console.log(stats);
  });
</script>

<svelte:head>
  <title>{series_name} | Mario Kart Central</title>
</svelte:head>

{#if series}
  <SeriesInfo {series} />
  <SeriesPosts {series}/>
  <SeriesPodiums {tournaments} />
  <SeriesStats {stats} />
{:else if not_found}
  {$LL.TOURNAMENTS.SERIES.NOT_FOUND()}
{/if}
