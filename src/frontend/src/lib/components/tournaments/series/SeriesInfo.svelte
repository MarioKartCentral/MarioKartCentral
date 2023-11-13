<script lang="ts">
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import LinkButton from "$lib/components/common/LinkButton.svelte";

    export let series: TournamentSeries;
</script>

<Section header="Series Info">
    <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/tournaments/series">Back to Series Listing</LinkButton>
    </div>
    <div class="container">
        {#if series.logo}
            <div class="img">
                <img src={series.logo} alt={series.series_name}/>
            </div>
        {/if}
        {series.description}
    </div>
</Section>

<style>
    .container {
        width: 100%;
    }
    img {
        margin: auto;
        max-width: 400px;
        max-height: 200px;
    }
</style>