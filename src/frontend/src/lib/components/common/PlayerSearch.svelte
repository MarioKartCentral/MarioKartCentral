<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import { createEventDispatcher } from 'svelte';
  import Table from './Table.svelte';
  import LL from '$i18n/i18n-svelte';
  import Flag from './Flag.svelte';
  import { UserAddSolid } from 'flowbite-svelte-icons';
  import CancelButton from './buttons/CancelButton.svelte';

  export let player: PlayerInfo | null = null;
  export let fc_type: string | null = null;
  export let registration_id: number | null = null;
  export let is_shadow: boolean | null = false;
  export let include_shadow_players = false;
  export let has_connected_user: boolean | null = null;
  export let is_banned: boolean | null = null;
  export let show_add_button: boolean = true;
  export let query = '';

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
    if (!query) {
      results = [];
      return;
    }
    let query_parameters = [];
    query_parameters.push('detailed=true');
    query_parameters.push('matching_fcs_only=true');
    query_parameters.push(`include_shadow_players=${include_shadow_players}`);
    if (query) {
      query_parameters.push(`name_or_fc=${query}`);
    }
    if (fc_type) {
      query_parameters.push(`fc_type=${fc_type}`);
    }
    if (registration_id) {
      query_parameters.push(`registration_id=${registration_id}`);
    }
    if (is_shadow !== null) {
      query_parameters.push(`is_shadow=${is_shadow}`);
    }
    if (has_connected_user !== null) {
      query_parameters.push(`has_connected_user=${has_connected_user}`);
    }
    if (is_banned !== null) {
      query_parameters.push(`is_banned=${is_banned}`);
    }
    const query_string = query_parameters.length ? query_parameters.join('&') : '';

    const url = `/api/registry/players?${query_string}`;
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      results = body['player_list'];
    }
  }

  function toggle_results(value: boolean) {
    // 100ms timeout if closing results so that clicking an option goes through
    setTimeout(() => (show_results = value), show_results ? 200 : 0);
  }

  function set_option(option: PlayerInfo | null) {
    player = option;
    dispatch('change'); // do this so we can run an on:change handler in parent component
  }
</script>

<div class="container" on:focusin={() => toggle_results(true)} on:focusout={() => toggle_results(false)}>
  {#if !player}
    <input type="search" placeholder={$LL.PLAYERS.LIST.SEARCH_BY()} bind:value={query} on:input={handle_search} />
    {#if show_results}
      <div class="table-outer">
        <div class="table-inner">
          <Table show_padding={false}>
            <col class="country" />
            <col class="name" />
            <col class="mobile-hide fc" />
            <col class="select" />
            <tbody>
              {#each results as result}
                <tr on:click={() => set_option(result)} title="Player ID: {result.id}">
                  <td on:click={() => set_option(result)}>
                    <Flag country_code={result.country_code} />
                  </td>
                  <td on:click={() => set_option(result)}>
                    {result.name}
                  </td>
                  <td class="mobile-hide" on:click={() => set_option(result)}>
                    {#if result.friend_codes.length}
                      {result.friend_codes[0].fc}
                    {/if}
                  </td>
                  <td on:click={() => set_option(result)}>
                    {#if show_add_button}
                      <UserAddSolid size="lg" />
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </Table>
        </div>
      </div>
    {/if}
  {:else}
    <div>
      <Flag country_code={player.country_code} />
      {player.name}
      <CancelButton on:click={() => set_option(null)} />
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
  div.table-outer {
    position: absolute;
    width: 100%;
    background-color: black;
    z-index: 1;
  }
  div.table-inner {
    max-height: 150px;
    overflow-y: scroll;
  }
  tr {
    cursor: pointer;
  }
  col.country {
    width: 15%;
  }
  col.name {
    width: 30%;
  }
  col.fc {
    width: 40%;
  }
  col.select {
    width: 15%;
  }
</style>
