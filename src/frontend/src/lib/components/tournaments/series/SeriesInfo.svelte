<script lang="ts">
  import { onMount } from 'svelte';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TypeBadge from '$lib/components/badges/TypeBadge.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { series_permissions } from '$lib/util/util';
  import SeriesPermissionCheck from '$lib/components/common/SeriesPermissionCheck.svelte';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import SeriesInfoList from './SeriesInfoList.svelte';
  import SeriesStats from './SeriesStats.svelte';

  export let series: TournamentSeries;
  export let tournaments = [];
  onMount(async () => {
    const res = await fetch(`/api/tournaments/series/${series.id}/placements`);
    if (res.status === 200) {
      const body = await res.json();
      const tab = [];
      for (let t of body) {
        tab.push(t);
      }
      tournaments = tab;
    }
  });
</script>

<Section header={series.series_name}>
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
    <div class="sub_container">
      <div class="seriesInfoBadge">
        <GameBadge game={series.game} />
      </div>
      <div class="seriesInfoBadge">
        <ModeBadge mode={series.mode} />
      </div>
      <div class="seriesInfoBadge">
        <TypeBadge type={'Squad'} />
      </div>
    </div>
    <MarkdownBox content={series.description} />
  </div>
</Section>
<Section header="Tournament History">
  <SeriesInfoList {tournaments} />
</Section>
<Section header="Stats">
  <SeriesStats {tournaments} />
</Section>

<style>
  .container {
    text-align: center;
    display: grid;
    background-color: rgba(24, 82, 28, 0.8);
    padding-top: 10px;
    padding-bottom: 10px;
    margin: 10px auto 10px auto;
  }
  img {
    margin-left: auto;
    margin-right: auto;
    display: block;
    max-width: 400px;
    max-height: 200px;
  }
  .sub_container {
    margin: auto;
    display: flex;
  }
  .seriesInfoBadge {
    margin-right: 3px;
  }
</style>
