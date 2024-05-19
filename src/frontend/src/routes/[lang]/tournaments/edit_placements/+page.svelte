<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { onMount } from "svelte";
    import {dndzone} from "svelte-dnd-action";
    import { page } from "$app/stores";
    import SoloPlacementsZone from "$lib/components/tournaments/placements/SoloPlacementsZone.svelte";

    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentSquad } from "$lib/types/tournament-squad";
    import type { TournamentPlayer } from "$lib/types/tournament-player";
    import type { TournamentPlacement } from "$lib/types/tournament-placement";
    import type { TournamentPlacementList } from "$lib/types/tournament-placement";

    let id = 0;
    //let tournament: Tournament;
    //let squad_registrations: TournamentSquad[] = [];
    //let solo_registrations: TournamentPlayer[] = [];
    let placements: TournamentPlacementList;
    let is_loaded = false;

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);

        // const res1 = await fetch(`/api/tournaments/${id}`);
        // if(res1.status !== 200) return;
        // let tournament_body: Tournament = await res1.json();
        // tournament = tournament_body;

        // const res2 = await fetch(`/api/tournaments/${id}/registrations`);
        // if(res2.status !== 200) return;
        
        // if(tournament.is_squad) {
        //     let registrations_body: TournamentSquad[] = await res2.json();
        //     squad_registrations = registrations_body;
        // }
        // else {
        //     let registrations_body: TournamentPlayer[] = await res2.json();
        //     solo_registrations = registrations_body;
        // }

        const res = await fetch(`/api/tournaments/${id}/placements`);
        let placements_body: TournamentPlacementList = await res.json();
        placements = placements_body;
        //console.log(placements);
        is_loaded = true;
    });

    let itemLists = [
        [{
            "id": 1,
            "name": "Cynda"
        }],
        [
            {"id": 2,
                "name": "cynda2"
            }
        ]
    ]

    function handleSort(e: CustomEvent, i: number) {
        itemLists[i] = e.detail.items;
        itemLists = itemLists;
    }
</script>

{#if is_loaded}
    <Section header="Edit Placements">
        <!-- <section use:dndzone={{items: itemLists[0]}} on:consider={e => handleSort(e, 0)} on:finalize={e => handleSort(e, 0)}>
            {#each itemLists[0] as item(item.id)}
                <div>{item.name}</div>
            {/each}
        </section> -->
        <!-- {#if !tournament.is_squad} -->
            <SoloPlacementsZone tournament_id={placements.tournament_id} is_squad={placements.is_squad} placements={placements.placements}/>
        <!-- {/if} -->
    </Section>
    <Section header="Unplaced Teams">
        <!-- {#if !tournament.is_squad} -->
            <SoloPlacementsZone tournament_id={placements.tournament_id} is_squad={placements.is_squad} placements={placements.unplaced} is_placements={false}/>
        <!-- {/if} -->
        <!-- <section use:dndzone={{items: itemLists[1]}} on:consider={e => handleSort(e, 1)} on:finalize={e => handleSort(e, 1)}>
            {#each itemLists[1] as item(item.id)}
                <div>{item.name}</div>
            {/each}
        </section> -->
    </Section>
{/if}