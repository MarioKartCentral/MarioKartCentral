<script lang="ts">
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import SquadPlacementDisplay from "./SquadPlacementDisplay.svelte";
    import { createEventDispatcher } from "svelte";
    import Dropdown from "$lib/components/common/Dropdown.svelte";
    import DropdownItem from "$lib/components/common/DropdownItem.svelte";
    import { ChevronDownSolid } from "flowbite-svelte-icons";
    import LL from "$i18n/i18n-svelte";

    const dispatch = createEventDispatcher();

    export let placement: PlacementOrganizer;
    export let is_edit: boolean;
    export let is_homepage = false;

    $: rank_width = is_homepage ? 'w-[50px]' : 'w-[100px]'
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

    function editPlacement() {
        if(placement.placement === null || placement.placement < 1) {
            placement.placement = 1;
        }
        placement.is_disqualified = false;
        placement.bounded = false;
        placement.placement_lower_bound = null;
        placement.tie = false;
        dispatch("placement_change");
    }
</script>

<div class="flex {bg_class}">
    <div class="rank {rank_width}">
        {getPlacementText(placement)}
    </div>
    <div class="info">
        <SquadPlacementDisplay squad={placement.squad}/>
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
        {#if placement.placement !== null}
            <input type="number" bind:value={placement.placement} on:blur={editPlacement} class="w-16" minlength=1/>
        {/if}
    {/if}
    <div class="description {is_homepage ? 'hidden' : ''}">
        {#if placement.placement !== null}
            {#if is_edit}
                <input class="title" bind:value={placement.description} placeholder={$LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_TITLE()} maxlength=32/>
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
        border-bottom: 1px solid theme('colors.primary.600' / 30%);
        border-left: 1px solid theme('colors.primary.600' / 30%);
        border-right: 1px solid theme('colors.primary.600' / 30%);
        padding: 5px;
        font-size: 80%;
    }
    div.gold {
        background-color: rgba(255, 254, 149, 0.30);
        color: #fffab0;
    }
    div.silver {
        background-color: rgba(195, 255, 255, 0.3);
        color: #dcfffc;
    }
    div.bronze {
        background-color: rgba(255, 158, 110, 0.30);
        color: #ffcbae;
    }
    div.other {
        background-color: rgba(255, 255, 255, 0.1);
    }
    div.dq {
        background-color: rgba(255, 0, 0, 0.2);
    }
    .pointer {
        cursor: pointer;
    }
    .rank {
        display: block;
        text-align: center;
        font-size: 1.5em;
        font-weight: 600;
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