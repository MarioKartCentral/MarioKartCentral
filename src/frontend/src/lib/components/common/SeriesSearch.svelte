<script lang="ts">
  import type { TournamentSeries, TournamentSeriesBasic } from '$lib/types/tournaments/series/tournament-series';
  import { onMount } from 'svelte';
  import Table from './table/Table.svelte';
  import { createEventDispatcher } from 'svelte';
  import CancelButton from './buttons/CancelButton.svelte';
  import LL from '$i18n/i18n-svelte';

  export let option: TournamentSeries | null = null;
  export let series_id: number | null = null;
  export let lock = false;

  let query = '';
  let results: TournamentSeriesBasic[] = [];
  let timeout: number;
  let show_results = false;

  async function handle_search() {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(get_results, 300);
  }

  const dispatch = createEventDispatcher<{ change: null }>();

  async function get_series(id: number) {
    const res = await fetch(`/api/tournaments/series/${id}`);
    const body: TournamentSeries = await res.json();
    option = body;
  }

  onMount(async () => {
    if (series_id) {
      await get_series(series_id);
    } else {
      await get_results();
    }
  });

  async function get_results() {
    const name_var = query ? `?name=${query}` : ``;
    const res = await fetch(`/api/tournaments/series/list${name_var}`);
    if (res.status === 200) {
      const body: TournamentSeriesBasic[] = await res.json();
      results = body;
    }
  }

  function toggle_results() {
    // 100ms timeout if closing results so that clicking an option goes through
    setTimeout(() => (show_results = !show_results), show_results ? 100 : 0);
  }

  async function set_option(series: TournamentSeriesBasic | null) {
    series_id = series ? series.id : null;
    if (series) {
      await get_series(series.id);
    } else {
      option = null;
    }
    dispatch('change'); // do this so we can run an on:change handler in parent component
  }
</script>

<div class="container" on:focusin={toggle_results} on:focusout={toggle_results}>
  {#if !option}
    <input placeholder={$LL.TOURNAMENTS.SEARCH_SERIES()} bind:value={query} on:input={handle_search} />
    {#if show_results}
      <div class="table">
        <Table containerClass="rounded-none" data={results} let:item={result}>
          <tr on:click={() => set_option(result)}>
            <td>
              {#if result.logo}
                <img src={result.logo} alt={result.series_name} />
              {/if}
            </td>
            <td>
              {result.series_name}
            </td>
          </tr>
        </Table>
      </div>
    {/if}
  {:else}
    <div>
      {option.series_name}
      {#if !lock}
        <CancelButton on:click={() => set_option(null)} />
      {/if}
    </div>
  {/if}
</div>

<style>
  .container {
    width: 60%;
    position: relative;
  }
  input {
    width: 100%;
  }
  div.table {
    display: block;
    position: absolute;
    width: 100%;
    max-height: 100px;
    overflow-y: scroll;
    background-color: black;
    font-size: 1.5em;
  }
  tr {
    cursor: pointer;
  }
  img {
    max-height: 20px;
  }
</style>
