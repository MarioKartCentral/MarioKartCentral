<script lang="ts">
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import LL from '$i18n/i18n-svelte';

  export let series: TournamentSeries;
</script>

<Section header={series.series_name} href="/{$page.params.lang}/tournaments/series/details?id={series.id}">
  <div class="container">
    {#if series.logo}
      <div class="img">
        <a href="/{$page.params.lang}/tournaments/series/details?id={series.id}">
          <img src={series.logo} alt={series.series_name} />
        </a>
      </div>
    {/if}
    <div class="flex">
      <div class="inner">
        <GameBadge game={series.game} />
      </div>
      <div class="inner">
        <ModeBadge mode={series.mode} />
      </div>
    </div>
    <div class="description">
      <MarkdownBox content={series.description} />
      <hr />
      <a href="/{$page.params.lang}/tournaments/series/details?id={series.id}">{$LL.TOURNAMENTS.SERIES.MORE_DETAILS()}</a>
    </div>
  </div>
</Section>

<style>
  .container {
    width: 100%;
  }
  img {
    margin: auto;
    max-width: 300px;
    max-height: 200px;
    width: 100%;
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
