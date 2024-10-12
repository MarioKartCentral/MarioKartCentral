<script lang="ts">
    import type { Team } from "$lib/types/team";
    import type { TeamRoster } from "$lib/types/team-roster";
    import { createEventDispatcher } from "svelte";
    import Table from "./Table.svelte";
    import TagBadge from "../badges/TagBadge.svelte";
    import { UserAddSolid } from "flowbite-svelte-icons";
    import CancelButton from "./buttons/CancelButton.svelte";
    import GameBadge from "../badges/GameBadge.svelte";

    export let roster: TeamRoster | null = null;
    export let game: string | null = null;

    let query = "";
    let results: TeamRoster[] = [];
    let show_results = false;
    let timeout: number;

    const dispatch = createEventDispatcher();

    async function handle_search() {
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(get_results, 300);
    }

    async function get_results() {
        const name_var = query ? `name=${query}` : ``;
        const game_var = game ? `&game=${game}` : ``;
        const url = `/api/registry/teams?${name_var}${game_var}`;
        const res = await fetch(url);
        if (res.status === 200) {
            const body = await res.json();
            let team_list: Team[] = body;
            results = team_list.flatMap((t) => t.rosters);
        }
    }

    function toggle_results() {
        // 100ms timeout if closing results so that clicking an option goes through
        setTimeout(() => (show_results = !show_results), show_results ? 100 : 0);
    }

    function set_option(option: TeamRoster | null) {
        roster = option;
        dispatch('change'); // do this so we can run an on:change handler in parent component
    }
</script>

<div class="container" on:focusin={toggle_results} on:focusout={toggle_results}>
    {#if !roster}
        <input type="search" placeholder="Search for rosters..." bind:value={query} on:input={handle_search} />
        {#if show_results}
            <div class="table-outer">
                <div class="table-inner">
                    <Table show_padding={false}>
                        <col class="tag"/>
                        <col class="name"/>
                        <col class="game"/>
                        <col class="select"/>
                        <tbody>
                            {#each results as result}
                                <tr on:click={() => set_option(result)}>
                                    <td>
                                        <TagBadge tag={result.tag} color={result.color}/>
                                    </td>
                                    <td>
                                        {result.name}
                                    </td>
                                    <td>
                                        <GameBadge game={result.game}/>
                                    </td>
                                    <td>
                                        <UserAddSolid size="lg"/>
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
            <TagBadge tag={roster.tag} color={roster.color}/>
            {roster.name}
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
    div.table-outer {
      position: absolute;
      width: 100%;
      background-color: black;
      z-index: 1;
    }
    div.table-inner {
      max-height: 100px;
      overflow-y: scroll;
    }
    tr {
      cursor: pointer;
    }
    col.tag {
        width: 20%;
    }
    col.name {
      width: 40%;
    }
    col.game {
        width: 20%;
    }
    col.select {
      width: 20%;
    }
  </style>
  