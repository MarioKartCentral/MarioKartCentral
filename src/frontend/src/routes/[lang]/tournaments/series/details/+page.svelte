<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import SeriesInfo from '$lib/components/tournaments/series/SeriesInfo.svelte';
  import LL from '$i18n/i18n-svelte';
  import SeriesPosts from '$lib/components/tournaments/series/SeriesPosts.svelte';

  let id = 0;
  let series: TournamentSeries;
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
    const body: TournamentSeries = await res.json();
    series = body;
  });
</script>

<svelte:head>
  <title>{series_name} | Mario Kart Central</title>
</svelte:head>

{#if series}
  <SeriesInfo {series} />
  <SeriesPosts {series}/>
{:else if not_found}
  {$LL.TOURNAMENTS.SERIES.NOT_FOUND()}
{/if}
