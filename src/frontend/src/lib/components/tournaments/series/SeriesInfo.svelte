<script lang="ts">
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";
    import LinkButton from "$lib/components/common/LinkButton.svelte";
    import { series_permissions } from "$lib/util/util";
    import SeriesPermissionCheck from "$lib/components/common/SeriesPermissionCheck.svelte";
    import MarkdownBox from "$lib/components/common/MarkdownBox.svelte";
    
    export let series: TournamentSeries;
</script>

<Section header="Series Info">
    <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/tournaments/series">Back to Series Listing</LinkButton>
        <SeriesPermissionCheck series_id={series.id} permission={series_permissions.edit_series}>
            <LinkButton href="/{$page.params.lang}/tournaments/series/edit?id={series.id}">Edit Series</LinkButton>
        </SeriesPermissionCheck>
        <SeriesPermissionCheck series_id={series.id} permission={series_permissions.create_tournament}>
            <LinkButton href="/{$page.params.lang}/tournaments/series/create_tournament/select_template?id={series.id}">Create Tournament</LinkButton>
        </SeriesPermissionCheck>
        <SeriesPermissionCheck series_id={series.id} permission={series_permissions.create_tournament_template}>
            <LinkButton href="/{$page.params.lang}/tournaments/series/templates?id={series.id}">Manage Templates</LinkButton>
        </SeriesPermissionCheck>
    </div>
    <div class="container">
        {#if series.logo}
            <div class="img">
                <img src={series.logo} alt={series.series_name}/>
            </div>
            
        {/if}
        <MarkdownBox content={series.description}/>
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