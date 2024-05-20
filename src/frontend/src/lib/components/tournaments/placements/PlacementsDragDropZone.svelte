<script lang="ts">
    import type { TournamentPlacement, TournamentPlacementSimple } from "$lib/types/tournament-placement";
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import {dndzone} from "svelte-dnd-action";
    import PlacementItem from "./PlacementItem.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    export let tournament_id: number;
    export let is_squad: boolean;
    export let placements: TournamentPlacement[];
    export let is_placements = true;

    let placement_list: PlacementOrganizer[] = [];
    for(let placement of placements) {
        placement_list.push({id: placement.registration_id, placement: placement.placement,
            description: placement.placement_description, tie: false, player: placement.player,
            squad: placement.squad
        })
    }

    if(is_placements) {
        placement_list.sort((a, b) => Number(a.placement) - Number(b.placement));
        for(let i = 1; i < placement_list.length; i++) {
            let curr = placement_list[i];
            let prev = placement_list[i-1];
            if(curr.placement === prev.placement) {
                curr.tie = true;
            }
        }
    }

    async function savePlacements() {
        let new_placements: TournamentPlacementSimple[] = [];
        // convert our placement list into the format used by the API
        for(let p of placement_list) {
            if(p.placement) {
                new_placements.push({registration_id: p.id, placement: p.placement, placement_description: p.description});
            }
        }
        const endpoint = `/api/tournaments/${tournament_id}/placements/set`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(new_placements),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Editing placements failed: ${result['title']}`);
        }
    }

    function updatePlacements() {
        // if this section is used for placements, update any ties as needed
        if(is_placements) {
            let curr_placement = 1;
            for(let i = 0; i < placement_list.length; i++) {
                let p = placement_list[i];
                if(p.tie) {
                    p.placement = curr_placement;
                }
                else {
                    p.placement = i+1;
                    curr_placement = i+1;
                }
            }
        }
        // otherwise if this is an unplaced section, set placement/description to null
        else {
            for(let i = 0; i < placement_list.length; i++) {
                let p = placement_list[i];
                p.placement = null;
                p.description = null;
                p.tie = false;
            }
        }
        placement_list = placement_list;
    }

    function handleSort(e: CustomEvent) {
        placement_list = e.detail.items;
        updatePlacements();
        
    }
</script>

<section class="zone" use:dndzone={{items: placement_list}} on:consider={e => handleSort(e)} on:finalize={e => handleSort(e)}>
    {#each placement_list as p(p.id)}
        <PlacementItem placement={p} {is_squad} on:change={updatePlacements}/>
    {/each}
    
</section>

{#if is_placements}
    <Button on:click={savePlacements}>Save</Button>
{/if}

<style>
    .zone {
        min-height: 50px;
        margin-bottom: 20px;
    }
</style>