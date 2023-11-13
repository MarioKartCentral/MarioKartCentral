<script lang="ts">
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";
    import Section from "$lib/components/common/Section.svelte";
    import { page } from "$app/stores";

    export let series: TournamentSeries;
</script>

<Section header={series.series_name} href="/{$page.params.lang}/tournaments/series/details?id={series.id}">
    <div class="container">
        {#if series.logo}
            <div class="img">
                <a href="/{$page.params.lang}/tournaments/series/details?id={series.id}">
                    <img src={series.logo} alt={series.series_name}/>
                </a>
            </div>
        {/if}
        <div class="flex">
            <div class="inner">
                {series.game}
            </div>
            <div class="inner">
                {series.mode}
            </div>
        </div>
        <div class="description">
            {series.description}
            <hr>
            <a href="/{$page.params.lang}/tournaments/series/details?id={series.id}">
                More Details
            </a>
        </div>
        
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
    .flex {
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 5px 0;
    }
    .inner {
        margin: 0 5px;
    }
    .description {
        max-width: 600px;
        margin: auto;
    }
    hr {
        margin: 10px 0;
    }
  </style>