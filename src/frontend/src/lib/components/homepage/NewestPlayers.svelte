<script lang="ts">
    import { page } from "$app/stores";
    import Section from "../common/Section.svelte";
    import LL from "$i18n/i18n-svelte";
    import { onMount } from "svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import Flag from "../common/Flag.svelte";

    let latestPlayers: PlayerInfo[] = []

    async function fetchLatestPlayers() {
    const res = await fetch(`/api/registry/players?is_hidden=false&matching_fcs_only=false&include_shadow_players=false&sort_by_newest=true`);
    console.log(res.status)
    if (res.status === 200) {
        const body = await res.json();
        latestPlayers = body.player_list.slice(0, 10)
        console.log(JSON.stringify(latestPlayers))
    }
    }

    onMount(fetchLatestPlayers)
</script>

<!-- TODO: localization -->
<Section header={'Newest Players'}>
    {#if latestPlayers.length}
        <div class="flex flex-col gap-[5px]">
            {#each latestPlayers as player, i}
                <div class="row">
                    <div class="flag">
                        <Flag country_code={player.country_code}/>
                    </div>
                    <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">{player.name}</a>
                </div>
            {/each}
        </div>
        <a
            class="hover:text-emerald-400 p-1 mt-[10px]"
            href="/{$page.params.lang}/registry/players">
            {'View All Players'}
        </a>
    {:else}
        {'No Players'}
    {/if}
</Section>

<style>
    .row {
        display: flex;
        font-size: 0.9rem;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 0px 10px;
        height: 20px;
        align-items: center;
        gap: 10px;
    }
    .flag {
        zoom: 85%;
    }
</style>