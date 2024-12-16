<script lang="ts">
    import Flag from "$lib/components/common/Flag.svelte";
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import SquadPlacementDisplay from "./SquadPlacementDisplay.svelte";
    import { page } from "$app/stores";
    import { createEventDispatcher } from "svelte";
    import Dropdown from "$lib/components/common/Dropdown.svelte";
    import DropdownItem from "$lib/components/common/DropdownItem.svelte";
    import { ChevronDownSolid } from "flowbite-svelte-icons";
    import LL from "$i18n/i18n-svelte";

    const dispatch = createEventDispatcher();

    export let placement: PlacementOrganizer;
    export let is_squad: boolean;
    export let is_edit: boolean;

    let bg_class = "other";
    $: {
        bg_class = "other";
        if(placement.is_disqualified) {
            bg_class = "dq";
        }
        else if(placement.placement === 1) {
            bg_class = "gold";
        }
        else if(placement.placement === 2) {
            bg_class = "silver";
        }
        else if(placement.placement === 3) {
            bg_class = "bronze";
        };
    }
    function getPlacementChar(num: number | null) {
        if(num === null) {
            return "-";
        }
        if(num === 1) {
            return "👑";
        }
        if(num === 2) {
            return "🥈";
        }
        if(num === 3) {
            return "🥉";
        }
        return num;
    }

    function getPlacementText(placement: PlacementOrganizer) {
        if(placement.is_disqualified) {
            return "DQ";
        }
        let text = getPlacementChar(placement.placement);
        if(placement.placement_lower_bound) {
            text += " - " + getPlacementChar(placement.placement_lower_bound);
        }
        return text;
    }

    function toggleDQ() {
        placement.is_disqualified = !placement.is_disqualified;
        if(placement.is_disqualified) {
            placement.placement = null;
            placement.bounded = false;
            placement.placement_lower_bound = null;
            placement.tie = false;
        }
        dispatch("dq");
    }
</script>

<div class="flex {bg_class}">
    <div class="rank">
        {getPlacementText(placement)}
    </div>
    <div class="info">
        {#if !is_squad && placement.player}
            <a href="/{$page.params.lang}/registry/players/profile?id={placement.player.player_id}">
                <Flag country_code={placement.player.country_code} size="small"/>
                {placement.player.name}
            </a>
        {:else if is_squad && placement.squad}
            <SquadPlacementDisplay squad={placement.squad}/>
        {/if}
    </div>
    {#if is_edit}
        <div class="actions">
            {$LL.COMMON.ACTIONS()}
            <ChevronDownSolid/>
        </div>
        <Dropdown>
            <DropdownItem>
                <label for="tie">{$LL.TOURNAMENTS.PLACEMENTS.TIE()}</label>
                <input id="tie" type="checkbox" bind:checked={placement.tie} on:change/>
            </DropdownItem>
            <DropdownItem>
                <label for="bound">{$LL.TOURNAMENTS.PLACEMENTS.LOWER_BOUND()}</label>
                <input id="bound" type="checkbox" bind:checked={placement.bounded} on:change/>
            </DropdownItem>
            <DropdownItem on:click={toggleDQ}>
                {$LL.TOURNAMENTS.PLACEMENTS.TOGGLE_DQ()}
            </DropdownItem>
        </Dropdown>
    {/if}
    <div class="description">
        {#if placement.placement}
            {#if is_edit}
                <input class="title" bind:value={placement.description} placeholder={$LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_TITLE()}/>
            {:else if placement.description}
                {placement.description}
            {/if}
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
        font-size: 80%;
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
    div.dq {
        background-color: rgba(250, 5, 5, 0.6);
    }
    .pointer {
        cursor: pointer;
    }
    .rank {
        width: 100px;
        display: block;
        text-align: center;
        font-size: 1.75em;
    }
    .info {
        min-width: 150px;
        max-width: 400px;
    }
    .actions {
        display: flex;
        width: 200px;
        gap: 5px;
        cursor: pointer;
    }
    .description {
        width: 200px;
    }
    input.title {
        width: 150px;
    }
</style>