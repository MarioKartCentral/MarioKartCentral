<script lang="ts">
    import type { TournamentPlacement, TournamentPlacementSimple } from "$lib/types/tournament-placement";
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import {dndzone} from "svelte-dnd-action";
    import PlacementItem from "./PlacementItem.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { sort_placement_list } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";

    export let tournament_id: number;
    export let placements: TournamentPlacement[];
    export let is_placements = true;

    let placement_list: PlacementOrganizer[] = [];

    for(let placement of placements) {
        placement_list.push({id: placement.registration_id, placement: placement.placement,
            description: placement.placement_description, tie: false,
            bounded: placement.placement_lower_bound ? true : false,
            placement_lower_bound: placement.placement_lower_bound, is_disqualified: placement.is_disqualified,
            player: placement.player, squad: placement.squad
        })
    }

    if(is_placements) {
        //placement_list.sort((a, b) => Number(a.placement) - Number(b.placement));
        placement_list.sort((a, b) => sort_placement_list(a, b));
        for(let i = 1; i < placement_list.length; i++) {
            let curr = placement_list[i];
            let prev = placement_list[i-1];
            if(curr.placement === prev.placement && !curr.placement_lower_bound) {
                curr.tie = true;
            }
        }
    }

    async function savePlacements() {
        let new_placements: TournamentPlacementSimple[] = [];
        // convert our placement list into the format used by the API
        for(let p of placement_list) {
            if(p.placement || p.is_disqualified) {
                // if it's a solo tournament, we want to use player ID instead of registration ID
                // since you can't view tournament player IDs on frontend
                new_placements.push({registration_id: p.player ? p.player.player_id : p.id, placement: p.placement, placement_description: p.description,
                    placement_lower_bound: p.placement_lower_bound, is_disqualified: Boolean(p.is_disqualified)
                });
            }
        }
        const endpoint = `/api/tournaments/${tournament_id}/placements/set`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(new_placements),
        });
        console.log(new_placements);
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.PLACEMENTS.SAVE_PLACEMENTS_FAILED()}: ${result['title']}`);
        }
    }

    function updatePlacements() {
        // this runs every time a placement's order is changed or one
        // of its properties are changed, we need to make sure the
        // placement number as well as upper/lower placement bounds
        // and DQ status are consistent throughout the list.
        if(is_placements) {
            let curr_placement = 1;
            let last_bounded = false;
            let curr_bound: number | null = null;

            // find the index of the last non-disqualified placement
            // in our placement list
            let last_placement_index = 0;
            for(let i = placement_list.length - 1; i >= 0; i--) {
                let p = placement_list[i];
                if(!p.is_disqualified) {
                    last_placement_index = i;
                    break;
                }
            }

            for(let i = 0; i < placement_list.length; i++) {
                let p = placement_list[i];
                // if there's a non-DQ'd placement below the current one,
                // we want to set the current placement to be non-DQ'd
                if(p.is_disqualified) {
                    if(i < last_placement_index) {
                        p.is_disqualified = false;
                    }
                    // if current placement is DQ'd, false/null all fields
                    else {
                        p.tie = false;
                        p.bounded = false;
                        p.placement = null;
                        p.placement_lower_bound = null;
                        curr_bound = null;
                        last_bounded = false;
                        continue;
                    }
                }
                if(p.bounded) {
                    // if this is the first placement in a range of placements
                    if(!last_bounded) {
                        // find the last placement in our range (curr_bound)
                        for(let j = i+1; j < placement_list.length; j++) {
                            let p2 = placement_list[j];
                            if(!p2.bounded) {
                                break;
                            }
                            curr_bound = j+1;
                        }
                        curr_placement = i+1;
                        last_bounded = true;
                    }
                    // set placement upper bound and lower bound
                    p.placement = curr_placement;
                    p.placement_lower_bound = curr_bound;
                    p.tie = false;
                }
                else {
                    // prevent ties with upper/lower bound placements
                    // since those are their own thing
                    if(p.tie && !last_bounded) {
                        p.placement = curr_placement;
                    }
                    else {
                        p.tie = false;
                        p.placement = i+1;
                        curr_placement = i+1;
                    }
                    last_bounded = false;
                    curr_bound = null;
                    p.placement_lower_bound = null;
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
                p.bounded = false;
            }
        }
        placement_list = placement_list;
    }

    function handleSort(e: CustomEvent) {
        placement_list = e.detail.items;
        updatePlacements();
        
    }

    function handleDQ() {
        // sort our list to put DQ's last before running updatePlacements
        placement_list.sort((a, b) => sort_placement_list(a, b));
        updatePlacements();
    }
</script>

<section class="zone" use:dndzone={{items: placement_list}} on:consider={e => handleSort(e)} on:finalize={e => handleSort(e)}>
    {#each placement_list as p(p.id)}
        <PlacementItem placement={p} is_edit={true} on:change={updatePlacements} on:dq={handleDQ}/>
    {/each}
    
</section>

{#if is_placements}
    <Button on:click={savePlacements}>{$LL.COMMON.SAVE()}</Button>
{/if}

<style>
    .zone {
        min-height: 50px;
        margin-bottom: 20px;
    }
</style>