<script lang="ts">
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import type { TournamentSquad } from "$lib/types/tournament-squad";
    import { page } from "$app/stores";

    export let squad: TournamentSquad;
</script>

<div class="flex">
    {#if squad.tag || squad.players.length > 4}
        <div>
            <TagBadge tag={squad.tag} color={squad.color}/>
        </div>
    {/if}
    
    {#if squad.name}
        <div>
            {squad.name}
        </div>
        
    {:else}
        {#if squad.players.length <= 4}
            <div class="flex players">
                {#each squad.players as p}
                    <div class="name">
                        <a href="/{$page.params.lang}/registry/players/profile?id={p.player_id}">
                            <Flag country_code={p.country_code} size="small"/>
                            {p.name}
                        </a>
                    </div>
                {/each}
            </div>
        {:else}
            Squad {squad.id}
        {/if}
    {/if}
    
</div>

<style>
    .flex {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
    }
    .players {
        max-width: 225px;
    }
    .name {
        min-width: 75px;
    }
</style>