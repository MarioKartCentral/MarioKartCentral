<script lang="ts">
    import Flag from "$lib/components/common/Flag.svelte";
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import SquadPlacementDisplay from "./SquadPlacementDisplay.svelte";

    export let placement: PlacementOrganizer;
    export let is_squad: boolean;

    let bg_class = "other";
    $: {
        bg_class = "other";
        if(placement.placement === 1) {
            bg_class = "gold";
        }
        else if(placement.placement === 2) {
            bg_class = "silver";
        }
        else if(placement.placement === 3) {
            bg_class = "bronze";
        };
    }
    
</script>

<div class="flex {bg_class}">
    <div class="rank">
        {#if placement.placement}
            {#if placement.placement === 1}
            👑
            {:else if placement.placement === 2}
            🥈
            {:else if placement.placement === 3}
            🥉
            {:else}
            {placement.placement}
            {/if}
        {/if}
    </div>
    <div class="info">
        {#if !is_squad && placement.player}
            <Flag country_code={placement.player.country_code} size="small"/>
            {placement.player.name}
        {:else if is_squad && placement.squad}
            <SquadPlacementDisplay squad={placement.squad}/>
        {/if}
    </div>
    
    <div class="tie">
        {#if placement.placement}
            <div>
                Tie?
                <input type="checkbox" bind:checked={placement.tie} on:change/>
            </div>
        {/if}
    </div>
    <div class="description">
        {#if placement.placement}
            <input class="title" bind:value={placement.description} placeholder="Title"/>
        {/if}
    </div>
</div>

<style>
    div.flex {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        border-bottom: 1px solid black;
        border-left: 1px solid black;
        border-right: 1px solid black;
        padding: 5px;
    }
    div.gold {
        background-color: rgba(250, 209, 5, 0.6);
    }
    div.silver {
        background-color: rgba(255, 255, 255, 0.5);
    }
    div.bronze {
        background-color: rgba(255, 136, 0, 0.5);
    }
    div.other {
        background-color: rgba(255, 255, 255, 0.15);
    }
    .rank {
        width: 100px;
        display: block;
        text-align: center;
        font-size: 1.5em;
    }
    .rank-text {
        font-size: 0.75em;
        width: 50%;
        margin: auto;
    }
    .info {
        min-width: 200px;
        max-width: 400px;
        font-size: 80%;
    }
    .tie {
        width: 100px;
    }
    .description {
        width: 200px;
    }
    input.title {
        width: 150px;
    }
</style>