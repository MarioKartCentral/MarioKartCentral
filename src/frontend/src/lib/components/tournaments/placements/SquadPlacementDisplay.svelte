<script lang="ts">
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import Flag from "$lib/components/common/Flag.svelte";
    import type { TournamentSquad } from "$lib/types/tournament-squad";

    export let squad: TournamentSquad;
</script>

<div class="flex">
    <div>
        <TagBadge tag={squad.tag} color={squad.color}/>
    </div>
    
    {#if squad.name}
        <div>
            {squad.name}
        </div>
        
    {:else}
        {#if squad.players.length <= 4}
            <div class="flex players">
                {#each squad.players as p}
                    <div class="name">
                        <Flag country_code={p.country_code} size="small"/>
                        {p.name}
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
        justify-content: center;
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