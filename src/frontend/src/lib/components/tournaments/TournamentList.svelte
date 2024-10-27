<script lang="ts">
    import { onMount } from 'svelte';
    import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
    import type { TournamentList } from '$lib/types/tournament-list';
    import type { TournamentListItem } from '$lib/types/tournament-list-item';
    import Section from '$lib/components/common/Section.svelte';
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import { check_permission, series_permissions, tournament_permissions } from '$lib/util/permissions';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import { page } from '$app/stores';
    import LL from '$i18n/i18n-svelte';
    import PageNavigation from '$lib/components/common/PageNavigation.svelte';
    import GameModeSelect from '../common/GameModeSelect.svelte';

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    let totalTournaments = 0;
    let totalPages = 0;
    let currentPage = 1;

    let game: string | null = null;
    let mode: string | null = null;
    let from: string | null = null;
    let to: string | null = null;
    let name: string | null = null;
    let show_hidden: boolean | null = null;

    let tournaments: TournamentListItem[] = [];

    async function fetchData() {
        let url = `/api/tournaments/list?page=${currentPage}`;
        if(game !== null) {
            url += `&game=${game}`;
        }
        if(mode !== null) {
            url += `&mode=${mode}`;
        }
        if(from) {
            url += `&from_date=${new Date(from).getTime()/1000}`;
        }
        if(to) {
            url += `&to_date=${new Date(to).getTime()/1000}`;
        }
        if(name) {
            url += `&name=${name}`;
        }
        if(show_hidden !== null) {
            url += `&is_public=${show_hidden}`;
        }
        const res = await fetch(url);
        if (res.status === 200) {
            const body: TournamentList = await res.json();
            tournaments = body.tournaments;
            totalTournaments = body.tournament_count;
            totalPages = body.page_count;
        }
    }

    onMount(fetchData);
</script>

<Section header={$LL.NAVBAR.TOURNAMENTS()}>
    <div slot="header_content">
        {#if check_permission(user_info, series_permissions.create_tournament)}
            <Button href="/{$page.params.lang}/tournaments/create/select_template">Create Tournament</Button>
        {/if}
    </div>
    <form on:submit|preventDefault={fetchData}>
        <div class="flex">
            <GameModeSelect bind:game={game} bind:mode={mode} flex all_option inline/>
            <div class="option">
                <div>
                    <label for="name">Name</label>
                </div>
                <div>
                    <input name="name" bind:value={name} placeholder="Search for tournaments..."/>
                </div>     
            </div>
            <div class="option">
                <div>
                    <label for="from">From</label>
                </div>
                <div>
                    <input name="from" type="datetime-local" bind:value={from}/>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="to">To</label>
                </div>
                <div>
                    <input name="to" type="datetime-local" bind:value={to}/>
                </div>
            </div>
            
            
            {#if check_permission(user_info, tournament_permissions.view_hidden_tournament)}
                <div class="option">
                    <div>
                        <label for="show_hidden"/>
                    </div>
                    <select bind:value={show_hidden}>
                        <option value={null}>Show hidden/private tournaments</option>
                        <option value={true}>Public tournaments only</option>
                        <option value={false}>Hidden/private tournaments only</option>
                    </select>
                </div>
            {/if}
        </div>
        <div class="centered">
            <Button type="submit">Filter</Button>
        </div>
    </form>
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
    <div>
        {totalTournaments} Tournaments
    </div>
    {#key tournaments}
        {#each tournaments as tournament}
            <TournamentPageItem {tournament} />
        {/each}
    {/key}
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
</Section>

<style>
    div.flex {
        align-items: center;
        flex-wrap: wrap;
        gap: 5px;
    }
    div.option {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
    input {
        width: 200px;
    }
    div.centered {
        text-align: center;
        margin: auto auto 10px auto;
    }
    :global(label) {
        margin-left: 5px;
        margin-right: 10px;
        display: inline-block;
        width: 50px;
    }
</style>