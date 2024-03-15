<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import { createEventDispatcher } from 'svelte';
  import Table from './Table.svelte';
  import LL from '$i18n/i18n-svelte';
  import Flag from './Flag.svelte';
  import { UserAddSolid } from 'flowbite-svelte-icons';
  import CancelButton from './CancelButton.svelte';

  export let player: PlayerInfo | null = null;
  export let game: string | null = null;
  export let squad_id: number | null = null;

  let query = '';
  let results: PlayerInfo[] = [];
  let timeout: number;
  let show_results = false;

  async function handle_search() {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(get_results, 300);
  }

  const dispatch = createEventDispatcher();

  async function get_results() {
    const name_var = query ? `&name_or_fc=${query}` : ``;
    const game_var = game ? `&game=${game}` : ``;
    const squad_var = squad_id ? `&squad_id=${squad_id}` : ``;
    const url = `/api/registry/players?detailed=true${name_var}${game_var}${squad_var}`;
    console.log(url);
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      results = body['player_list'];
    }
  }

  function toggle_results() {
    // 100ms timeout if closing results so that clicking an option goes through
    setTimeout(() => (show_results = !show_results), show_results ? 100 : 0);
  }

  function set_option(option: PlayerInfo | null) {
    player = option;
    dispatch('change'); // do this so we can run an on:change handler in parent component
  }
</script>

<div class="container" on:focusin={toggle_results} on:focusout={toggle_results}>
  {#if !player}
    <input type="search" placeholder={$LL.PLAYER_LIST.FILTERS.SEARCH_BY()} bind:value={query} on:input={handle_search} />
    {#if show_results}
      <div class="table">
        <Table show_padding={false}>
          <col class="country" />
          <col class="name" />
          <col class="mobile-hide fc" />
          <col class="select"/>
          <tbody>
            {#each results as result}
              <tr on:click={() => set_option(result)}>
                <td>
                  <Flag country_code={result.country_code}/>
                </td>
                <td>
                  {result.name}
                </td>
                <td class="mobile-hide">
                  {#if result.friend_codes.length}
                    {result.friend_codes[0].fc}
                  {/if}
                </td>
                <td>
                  <UserAddSolid size="lg"/>
                </td>
              </tr>
            {/each}
          </tbody>
          
        </Table>
      </div>
    {/if}
  {:else}
    <div>
      <Flag country_code={player.country_code}/>
      {player.name}
      <CancelButton on:click={() => set_option(null)}/>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 400px;
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
  col.country {
    width: 20%;
  }
  col.name {
    width: 30%;
  }
  col.fc {
    width: 30%;
  }
  col.select {
    width: 20%;
  }
</style>
