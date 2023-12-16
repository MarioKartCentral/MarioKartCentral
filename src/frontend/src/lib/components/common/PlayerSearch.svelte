<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import type { PlayerFilter } from "$lib/types/registry/players/player-filter";
    import { createEventDispatcher } from 'svelte';
    import Table from "./Table.svelte";

    export let player: PlayerInfo | null = null;
    export let game: string | null = null;

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
        const game_var = game ? `&game=${game}`: ``;
        const url = `/api/registry/players?detailed=true${name_var}${game_var}`;
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
    <input placeholder="Search for players..." bind:value={query} on:input={handle_search} />
    {#if show_results}
    <div class="table">
        <Table show_padding={false}>
            <col class="country"/>
            <col class="name"/>
            <col class="fc"/>
            {#each results as result, i}
                <tr on:click={() => set_option(result)}>
                    <td>
                        {result.country_code}
                    </td>
                    <td>
                        {result.name}
                    </td>
                    <td>
                        {#if result.friend_codes.length}
                            {result.friend_codes[0].fc}
                        {/if}
                    </td>
                </tr>
            {/each}
        </Table>
    </div>
    {/if}
{:else}
    <div>
        {player.name}
        <button on:click={() => set_option(null)}>X</button>
    </div>
{/if}
</div>

<style>
    .container {
      width: 40%;
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
        width: 10%;
    }
    col.name {
        width: 50%;
    }
    col.fc {
        width: 40%;
    }
</style>
  