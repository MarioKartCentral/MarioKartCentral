<script lang="ts">
    import type { TournamentListItem } from "$lib/types/tournament-list-item";
    import { onMount } from "svelte";
    import TournamentList from "../tournaments/TournamentList.svelte";
    import Section from "../common/Section.svelte";
    import { page } from '$app/stores';
    import TournamentPageItem from "../tournaments/TournamentPageItem.svelte";

    let tournaments: TournamentListItem[] = [];

    async function fetchLatestTournaments() {
        let url = `/api/tournaments/list`;
        const res = await fetch(url);
        if (res.status === 200) {
        const body: TournamentList = await res.json();
        tournaments = body.tournaments.slice(0, 7);
        }
    }

    onMount(fetchLatestTournaments)
</script>

<!-- TODO: localization -->
<Section header={'Latest Tournaments'}>
    <div class="h-[690px] m-[0]">
        {#key tournaments}
            {#each tournaments as tournament}
                <TournamentPageItem {tournament} />
            {/each}
        {/key}
        <a
            class="hover:text-emerald-400 p-1"
            href="/{$page.params.lang}/tournaments">
            {'View All Tournaments'}
        </a>
    </div>
</Section>