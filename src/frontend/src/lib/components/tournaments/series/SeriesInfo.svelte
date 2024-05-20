<script lang="ts">
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { series_permissions } from '$lib/util/util';
  import SeriesPermissionCheck from '$lib/components/common/SeriesPermissionCheck.svelte';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';

  export let series: TournamentSeries;
</script>

<Section header="Series Info">
  <div slot="header_content">
    <Button href="/{$page.params.lang}/tournaments/series">Back to Series Listing</Button>
    <SeriesPermissionCheck series_id={series.id} permission={series_permissions.edit_series}>
      <Button href="/{$page.params.lang}/tournaments/series/edit?id={series.id}">Edit Series</Button>
    </SeriesPermissionCheck>
    <SeriesPermissionCheck series_id={series.id} permission={series_permissions.create_tournament}>
      <Button href="/{$page.params.lang}/tournaments/series/create_tournament/select_template?id={series.id}"
        >Create Tournament</Button
      >
    </SeriesPermissionCheck>
    <SeriesPermissionCheck series_id={series.id} permission={series_permissions.create_tournament_template}>
      <Button href="/{$page.params.lang}/tournaments/series/templates?id={series.id}">Manage Templates</Button>
    </SeriesPermissionCheck>
  </div>
  <div class="container">
    {#if series.logo}
      <div class="img">
        <img src={series.logo} alt={series.series_name} />
      </div>
    {/if}
    <MarkdownBox content={series.description} />
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
