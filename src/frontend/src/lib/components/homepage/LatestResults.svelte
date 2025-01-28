<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import { onMount } from "svelte";
    import PlacementsDisplay from "../tournaments/placements/PlacementsDisplay.svelte";
    import Section from "../common/Section.svelte";

    let latestTournament: Tournament | null = null;

    async function fetchLatestTournamentWithPlacements() {
        const res = await fetch(`/api/tournaments/latestWithPlacements`);
        if (res.status === 200) {
            const body: Tournament = await res.json();
            latestTournament = body
        }
    }

    onMount(fetchLatestTournamentWithPlacements)
</script>

<!-- TODO: localization -->
{#if latestTournament}
    <PlacementsDisplay tournament={latestTournament} is_Homepage={true}/>
{:else}
    <Section header={'Latest Results'}>
        None
    </Section>
{/if}