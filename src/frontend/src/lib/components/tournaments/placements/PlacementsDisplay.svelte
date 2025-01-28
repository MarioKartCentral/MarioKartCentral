<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { PlacementOrganizer } from "$lib/types/placement-organizer";
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentPlacementList } from "$lib/types/tournament-placement";
    import { onMount } from "svelte";
    import PlacementItem from "./PlacementItem.svelte";
    import { sort_placement_list } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";
  import { page } from '$app/stores';

    export let tournament: Tournament;
    export let is_Homepage = false;
    let placements: TournamentPlacementList;
    let placement_list: PlacementOrganizer[] = [];
    let show_all = false;
    let num_display = 12;

    onMount(async() => {
        const res = await fetch(`/api/tournaments/${tournament.id}/placements`);
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
        placement_list = placement_list;
    });
</script>

{#if placement_list.length}
    {#if is_Homepage}
        <!-- TODO: localization -->
        <Section header={'Latest Results'}>
            <div slot="header_content">
                <!-- TODO: make list scrollable -->
                {#if placement_list.length > num_display}
                    <button on:click={() => show_all = !show_all}>
                        ({show_all ? "Hide" : "Show"} all)
                    </button>
                {/if}
            </div>
            <div class="h-[700px] m-[0]">
                <a href="/{$page.params.lang}/tournaments/details/{tournament.id}">{tournament.name}</a>
                {#each show_all ? placement_list : placement_list.slice(0, num_display) as placement}
                    <PlacementItem {placement} is_squad={tournament.is_squad} is_edit={false}/>
                {/each}
            </div>
        </Section>
    {:else}
        <Section header={$LL.TOURNAMENTS.TOURNAMENT_PLACEMENTS()}>
            <div slot="header_content">
                {#if placement_list.length > num_display}
                    <button on:click={() => show_all = !show_all}>
                        ({show_all ? "Hide" : "Show"} all)
                    </button>
                {/if}
            </div>
            {#each show_all ? placement_list : placement_list.slice(0, num_display) as placement}
                <PlacementItem {placement} is_squad={tournament.is_squad} is_edit={false}/>
            {/each}
        </Section>
    {/if}
{/if}