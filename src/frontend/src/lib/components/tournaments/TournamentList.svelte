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

    async function search() {
        currentPage = 1;
        fetchData();
    }

    onMount(fetchData);
</script>

<Section header={$LL.NAVBAR.TOURNAMENTS()}>
    <div slot="header_content">
        {#if check_permission(user_info, series_permissions.create_tournament)}
            <Button href="/{$page.params.lang}/tournaments/create/select_template">{$LL.TOURNAMENTS.CREATE_TOURNAMENT()}</Button>
        {/if}
    </div>
    <form on:submit|preventDefault={search}>
        <div class="flex">
            <div class="option">
                <GameModeSelect bind:game={game} bind:mode={mode} flex all_option inline/>
            </div>
            
            <div class="option">
                <div>
                    <label for="name">{$LL.COMMON.NAME()}</label>
                </div>
                <div>
                    <input name="name" bind:value={name} placeholder={$LL.TOURNAMENTS.SEARCH_FOR_TOURNAMENTS()}/>
                </div>     
            </div>
            <div class="option">
                <div>
                    <label for="from">{$LL.COMMON.FROM()}</label>
                </div>
                <div>
                    <input name="from" type="datetime-local" bind:value={from}/>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="to">{$LL.COMMON.TO()}</label>
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
                        <option value={null}>{$LL.TOURNAMENTS.SHOW_HIDDEN_PRIVATE_TOURNAMENTS()}</option>
                        <option value={true}>{$LL.TOURNAMENTS.PUBLIC_TOURNAMENTS_ONLY()}</option>
                        <option value={false}>{$LL.TOURNAMENTS.HIDDEN_PRIVATE_TOURNAMENTS_ONLY()}</option>
                    </select>
                </div>
            {/if}
        </div>
        <div class="centered">
            <Button type="submit">{$LL.COMMON.FILTER()}</Button>
        </div>
    </form>
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
    <div>
        {$LL.TOURNAMENTS.TOURNAMENT_COUNT({count: totalTournaments})}
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