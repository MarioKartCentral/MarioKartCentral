<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import { onMount } from "svelte";
    import Section from "../common/Section.svelte";
    import type { TournamentPlacementList } from "$lib/types/tournament-placement";
    import { sort_placement_list } from "$lib/util/util";
    import { page } from '$app/stores';
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import PlacementItem from "../tournaments/placements/PlacementItem.svelte";
    import HomeSectionContent from "./HomeSectionContent.svelte";

    let tournament: Tournament | null = null;
    let placements: TournamentPlacementList;
    let placement_list: PlacementOrganizer[] = [];

    async function fetchLatestTournamentWithPlacements() {
        const res = await fetch(`/api/tournaments/latestWithPlacements`);
        if (res.status === 200) {
            const body: Tournament = await res.json();
            tournament = body
            return body
        }
        return null
    }

    async function setPlacements(tournamentId: number) {
        const res = await fetch(`/api/tournaments/${tournamentId}/placements`);
        let placements_body: TournamentPlacementList = await res.json();
        placements = placements_body;
        for(let placement of placements.placements) {
            placement_list.push({id: placement.registration_id, placement: placement.placement,
                description: placement.placement_description, tie: false,
                bounded: placement.placement_lower_bound ? true : false,
                placement_lower_bound: placement.placement_lower_bound, is_disqualified: placement.is_disqualified,
                player: placement.player, squad: placement.squad
            })
        }
        placement_list.sort((a, b) => sort_placement_list(a, b));
        placement_list = placement_list.slice(0, 10);
    }

    onMount(async () => {
        const latestTournament = await fetchLatestTournamentWithPlacements()
        if (!latestTournament)
            return
        
        await setPlacements(latestTournament.id)
    });
</script>

<!-- TODO: localization -->
<Section header={'Latest Results'}>
    {#if tournament && placement_list}
        <HomeSectionContent isTopRow={true} link="/{$page.params.lang}/tournaments/details?id={tournament.id}" linkText="View Full Placements">
            {#if tournament.logo}
                <div class="flex w-full justify-center mt-[5px]">
                    <a 
                        href="/{$page.params.lang}/tournaments/details?id={tournament.id}"
                        class='flex w-[200px] h-[80px] justify-center'
                    >
                        <img src={tournament.logo} alt={tournament.name} class="max-w-full max-h-full" />
                    </a>
                </div>
            {/if}
            <div class="text-center mt-[15px] mb-[20px] font-bold">
                <a href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
                    {tournament.name}
                </a>
            </div>
            <div class="flex flex-col gap-[3px]">
                {#each placement_list as placement}
                    <PlacementItem {placement} is_squad={tournament.is_squad} is_edit={false} is_homepage={true}/>
                {/each}
            </div>
        </HomeSectionContent>
    {/if}
</Section>
