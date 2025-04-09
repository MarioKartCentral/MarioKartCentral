<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import { onMount } from "svelte";
    import type { TournamentPlacementList } from "$lib/types/tournament-placement";
    import { sort_placement_list } from "$lib/util/util";
    import { page } from '$app/stores';
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import PlacementItem from "../tournaments/placements/PlacementItem.svelte";
    import HomeSection from "./HomeSection.svelte";
    import { user } from "$lib/stores/stores";
    import LL from "$i18n/i18n-svelte";

    export let style: string;
    let tournament: Tournament | null = null;
    let placement_list: PlacementOrganizer[] = [];
    let playerPlacement: number | null = null;

    async function fetchLatestTournamentWithPlacements() {
        const res = await fetch(`/api/tournaments/latestWithPlacements`);
        if (res.status === 200) {
            const body: Tournament = await res.json();
            tournament = body;
            return body;
        }
        return null;
    }

    async function setPlacements(tournamentId: number) {
        const res = await fetch(`/api/tournaments/${tournamentId}/placements`);
        let placements_body: TournamentPlacementList = await res.json();
        const placements = placements_body;
        const tmp: PlacementOrganizer[] = [];
        for(let placement of placements.placements) {
            tmp.push({id: placement.registration_id, placement: placement.placement,
                description: placement.placement_description, tie: false,
                bounded: placement.placement_lower_bound ? true : false,
                placement_lower_bound: placement.placement_lower_bound, is_disqualified: placement.is_disqualified,
                player: placement.player, squad: placement.squad
            })
        }
        tmp.sort((a, b) => sort_placement_list(a, b));
        playerPlacement = getPlayerPlacement(tmp);
        placement_list = tmp.slice(0, 16);
    }

    function getPlayerPlacement(list: PlacementOrganizer[]) {
        const player = $user.player;
        if (!player)
            return null;
        
        for (let placement of list) {
            // ffa tournaments
            if (placement.player?.player_id === player.id)
                return placement.placement;

            // squad tournaments
            if (!placement.squad)
                return null;
            for (let p of placement.squad.players) {
                if (p.player_id === player.id)
                    return placement.placement;
            }
        }
        return null;
    }

    onMount(async () => {
        const latestTournament = await fetchLatestTournamentWithPlacements();
        if (!latestTournament)
            return;
        
        await setPlacements(latestTournament.id);
    });
</script>

<HomeSection 
    header={$LL.HOMEPAGE.LATEST_RESULTS()}
    link={tournament ? `/${$page.params.lang}/tournaments/details?id=${tournament.id}` : null}
    linkText={$LL.HOMEPAGE.VIEW_FULL_PLACEMENTS()}
    {style}
>
    {#if tournament && placement_list}
        {#if tournament.logo}
            <div class="flex w-full justify-center mt-[5px] mb-[10px]">
                <a 
                    href="/{$page.params.lang}/tournaments/details?id={tournament.id}"
                    class='flex w-[300px] h-[80px] justify-center'
                >
                    <img src={tournament.logo} alt={tournament.name} class="max-w-full max-h-full" />
                </a>
            </div>
        {/if}
        <div class="text-center font-bold">
            <a href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
                {tournament.name}
            </a>
        </div>
        {#if playerPlacement}
            <div class="text-center text-xl font-black">
                {$LL.HOMEPAGE.YOU_PLACED({placement: playerPlacement})}
            </div>
        {/if}
        <div class="flex flex-col {playerPlacement ? 'mt-[14px]' : 'mt-[13px]'}">
            {#each placement_list as placement}
                <PlacementItem {placement} is_squad={tournament.is_squad} is_edit={false} is_homepage={true}/>
            {/each}
        </div>
    {/if}
</HomeSection>
