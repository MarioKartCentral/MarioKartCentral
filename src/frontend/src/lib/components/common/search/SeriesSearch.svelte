<script lang="ts">
  import type { TournamentSeries, TournamentSeriesBasic } from '$lib/types/tournaments/series/tournament-series';
  import LL from '$i18n/i18n-svelte';
  import LazyLoad from '$lib/components/media/LazyLoad.svelte';
  import Search from './Search.svelte';

  export let series: TournamentSeries | null = null;
  export let disabled: boolean = false;
  export let id: string = 'series-search';
  export let ariaLabel: string | undefined = undefined;
  export let ariaLabelledby: string | undefined = undefined;

  let searchQuery: string;
  let results: TournamentSeriesBasic[] | undefined;
  let timeout: number;
  let container: HTMLUListElement;

  async function handleSearch() {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (!searchQuery) {
      results = undefined;
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
  {id}
  {ariaLabel}
  {ariaLabelledby}
  placeholder={$LL.TOURNAMENTS.SEARCH_SERIES()}
  bind:searchQuery
  bind:selected={series}
  bind:results
  let:option
  bind:container
  oninput={handleSearch}
  optionLabel={(option) => `ID: ${option.id}, ${option.series_name}`}
  {disabled}
>
  <div slot="selected" class="flex items-center gap-2" let:selected={series}>
    {#if series}
      {series.series_name}
    {/if}
  </div>
  <div class="w-[40px]">
    {#if option.logo}
      <LazyLoad>
        <img src={option.logo} alt={option.series_name} />
      </LazyLoad>
    {/if}
  </div>
  <div class="flex-1">
    {option.series_name}
  </div>
</Search>
