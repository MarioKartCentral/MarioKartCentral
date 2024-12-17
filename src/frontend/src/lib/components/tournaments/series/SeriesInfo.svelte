<script lang="ts">
  import { onMount } from 'svelte';
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import TypeBadge from '$lib/components/badges/TypeBadge.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import LL from '$i18n/i18n-svelte';
  import SeriesInfoList from './SeriesInfoList.svelte';
  import SeriesStats from './SeriesStats.svelte';
  import { makeMedalsRankings } from '$lib/util/stats';

  export let series: TournamentSeries;
  export let tournaments = [];
  export let teams = [];
  let podiums = [];

  onMount(async () => {
    const res = await fetch(`/api/tournaments/series/${series.id}/placements`);
    if (res.status === 200) {
      const body = await res.json();
      const tab = [];
      for (let t of body) {
        tab.push(t);
      }
      tournaments = tab;
      teams = makeMedalsRankings(tournaments)
    }
  });

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

</script>

<Section header={$LL.TOURNAMENTS.SERIES.SERIES_INFO()}>
  <div slot="header_content">
    <Button href="/{$page.params.lang}/tournaments/series">{$LL.TOURNAMENTS.SERIES.BACK_TO_SERIES_LISTING()}</Button>
    {#if check_series_permission(user_info, series_permissions.edit_series, series.id)}
      <Button href="/{$page.params.lang}/tournaments/series/edit?id={series.id}">{$LL.TOURNAMENTS.SERIES.EDIT()}</Button>
    {/if}
    {#if check_series_permission(user_info, series_permissions.create_tournament, series.id)}
      <Button href="/{$page.params.lang}/tournaments/series/create_tournament/select_template?id={series.id}"
        >{$LL.TOURNAMENTS.CREATE_TOURNAMENT()}</Button
      >
    {/if}
    {#if check_series_permission(user_info, series_permissions.create_tournament_template, series.id)}
      <Button href="/{$page.params.lang}/tournaments/series/templates?id={series.id}">{$LL.TOURNAMENTS.SERIES.MANAGE_TEMPLATES()}</Button>
    {/if}
    {#if check_series_permission(user_info, series_permissions.manage_series_roles, series.id)}
      <Button href="/{$page.params.lang}/tournaments/series/manage_roles?id={series.id}">{$LL.ROLES.MANAGE_ROLES()}</Button>
    {/if}
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
  <SeriesStats {teams} />
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
