<script lang="ts">
  import type { TournamentSeries, TournamentSeriesBasic } from '$lib/types/tournaments/series/tournament-series';
  import LL from '$i18n/i18n-svelte';
  import LazyLoad from '$lib/components/media/LazyLoad.svelte';
  import Search from './Search.svelte';

  export let series: TournamentSeries | null = null;
  export let disabled: boolean = false;

  let searchQuery: string;
  let results: TournamentSeriesBasic[];
  let timeout: number;
  let container: HTMLDivElement;

  async function handleSearch() {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (!searchQuery) {
      results = [];
      return;
    }
    timeout = setTimeout(getResults, 300);
  }

  async function getResults() {
    const res = await fetch(url);
    if (res.ok) {
      results = await res.json();
    }
  }

  $: url = (() => {
    const baseUrl = '/api/tournaments/series/list';
    if (searchQuery) return baseUrl + `?name=${searchQuery}`;
    return baseUrl;
  })();
</script>

<Search
  placeholder={$LL.TOURNAMENTS.SEARCH_SERIES()}
  bind:searchQuery
  bind:selected={series}
  bind:results
  let:result
  bind:container
  oninput={handleSearch}
  {disabled}
>
  <div slot="selected" class="flex items-center gap-2" let:selected={series}>
    {#if series}
      {series.series_name}
    {/if}
  </div>
  <td>
    {#if result.logo}
      <LazyLoad>
        <img src={result.logo} alt={result.series_name} />
      </LazyLoad>
    {/if}
  </td>
  <td>
    {result.series_name}
  </td>
</Search>
