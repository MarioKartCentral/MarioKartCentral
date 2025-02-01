<script lang="ts">
  import type { TournamentSeries } from '$lib/types/tournaments/series/tournament-series';
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import LL from '$i18n/i18n-svelte';

  export let series: TournamentSeries;

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
