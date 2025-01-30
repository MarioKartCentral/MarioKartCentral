<script lang="ts">
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";
    import { onMount } from "svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import Flag from "../common/Flag.svelte";
    import HomeSection from "./HomeSection.svelte";

    export let style: string;
    let innerWidth: number;
    let allLatestPlayers: PlayerInfo[] = []

    $: extend = 1025 <= innerWidth && innerWidth < 1280;
    $: latestPlayers = allLatestPlayers.slice(0, extend ? 11 : 10)

    async function fetchLatestPlayers() {
        const res = await fetch(`/api/registry/players?is_hidden=false&matching_fcs_only=false&include_shadow_players=false&sort_by_newest=true`);
        if (res.status === 200) {
            const body = await res.json();
            allLatestPlayers = body.player_list
        }
    }

    onMount(fetchLatestPlayers)
</script>

<svelte:window bind:innerWidth />

<HomeSection 
    header={$LL.HOMEPAGE.NEWEST_PLAYERS()} 
    link='/{$page.params.lang}/registry/players' 
    linkText={$LL.HOMEPAGE.VIEW_ALL_PLAYERS()}
    {style}
>
    {#if latestPlayers.length}
        <div class="flex flex-col {extend ? 'gap7' : 'gap-[5px]'}">
            {#each latestPlayers as player}
                <div class="row">
                    <div class="flag">
                        <Flag country_code={player.country_code}/>
                    </div>
                    <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">{player.name}</a>
                </div>
            {/each}
        </div>
    {/if}
</HomeSection>

<style>
    .row {
        display: flex;
        font-size: 0.9rem;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 0px 10px;
        height: 45px;
        align-items: center;
        gap: 10px;
    }
    .row:nth-child(odd) {
        background-color: rgba(210, 210, 210, 0.15);
    }
    .flag {
        zoom: 85%;
    }
    .gap7 {
        gap: 7px; /* tailwind has issue with gap-[7px] for some reason */
    }
</style>