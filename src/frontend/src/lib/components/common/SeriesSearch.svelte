<script lang="ts">
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import { onMount } from 'svelte';
  import Table from './Table.svelte';
  import { createEventDispatcher } from 'svelte';

  export let option: TournamentSeries | null = null;
  export let series_id: number | null = null;
  export let lock = false;

  let query = '';
  let results: TournamentSeries[] = [];
  let timeout: number;
  let show_results = false;

  async function handle_search() {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(get_results, 300);
  }

  const dispatch = createEventDispatcher();

  onMount(async () => {
    console.log(series_id);
    if (series_id) {
      const res = await fetch(`/api/tournaments/series/${series_id}`);
      const body: TournamentSeries = await res.json();
      option = body;
    } else {
      await get_results();
    }
  });

  async function get_results() {
    const name_var = query ? `?name=${query}` : ``;
    const res = await fetch(`/api/tournaments/series/list${name_var}`);
    if (res.status === 200) {
      const body: TournamentSeries[] = await res.json();
      results = body;
    }
  }

  function toggle_results() {
    // 100ms timeout if closing results so that clicking an option goes through
    setTimeout(() => (show_results = !show_results), show_results ? 100 : 0);
  }

  function set_option(series: TournamentSeries | null) {
    option = series;
    series_id = option ? option.id : null;
    dispatch('change'); // do this so we can run an on:change handler in parent component
  }
</script>

<div class="container" on:focusin={toggle_results} on:focusout={toggle_results}>
  {#if !option}
    <input placeholder="Search tournament series..." bind:value={query} on:input={handle_search} />
    {#if show_results}
      <div class="table">
        <Table show_padding={false}>
          {#each results as result, i}
            <tr on:click={() => set_option(result)}>
              {result.series_name}
            </tr>
          {/each}
        </Table>
      </div>
    {/if}
  {:else}
    <div>
      {option.series_name}
      {#if !lock}
        <button on:click={() => set_option(null)}>X</button>
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
    position: absolute;
    width: 100%;
    max-height: 80px;
    overflow-y: scroll;
    background-color: black;
  }
  tr {
    cursor: pointer;
  }
</style>
