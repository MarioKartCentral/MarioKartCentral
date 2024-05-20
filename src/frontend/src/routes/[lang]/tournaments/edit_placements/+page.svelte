<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import PlacementsDragDropZone from "$lib/components/tournaments/placements/PlacementsDragDropZone.svelte";

    import type { TournamentPlacementList } from "$lib/types/tournament-placement";

    let id = 0;
    let placements: TournamentPlacementList;
    let is_loaded = false;

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);

        const res = await fetch(`/api/tournaments/${id}/placements`);
        let placements_body: TournamentPlacementList = await res.json();
        placements = placements_body;
        is_loaded = true;
    });
</script>

{#if is_loaded}
    <Section header="Edit Placements">
        <PlacementsDragDropZone tournament_id={placements.tournament_id} is_squad={placements.is_squad} placements={placements.placements}/>
    </Section>
    <Section header="Unplaced Teams">
        <PlacementsDragDropZone tournament_id={placements.tournament_id} is_squad={placements.is_squad} placements={placements.unplaced} is_placements={false}/>
    </Section>
{/if}