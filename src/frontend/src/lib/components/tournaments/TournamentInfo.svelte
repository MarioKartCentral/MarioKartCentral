<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import { locale } from '$i18n/i18n-svelte';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import Section from '../common/Section.svelte';
  import Button from '../common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import GameBadge from '../badges/GameBadge.svelte';
  import TypeBadge from '../badges/TypeBadge.svelte';
  import ModeBadge from '../badges/ModeBadge.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import LL from '$i18n/i18n-svelte';

  export let tournament: Tournament;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let type = tournament.is_squad ? (tournament.teams_allowed ? $LL.TOURNAMENTS.TYPES.TEAM() : $LL.TOURNAMENTS.TYPES.SQUAD()) : $LL.TOURNAMENTS.TYPES.SOLO();
  let date_start = new Date(tournament.date_start * 1000);
  let date_end = new Date(tournament.date_end * 1000);
  let registration_deadline = tournament.registration_deadline
    ? new Date(tournament.registration_deadline * 1000)
    : null;
  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
    timeStyle: 'short',
    hour12: true,
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const game_strings: any = $LL.GAMES;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mode_strings: any = $LL.MODES;
</script>

<Section header={$LL.TOURNAMENTS.INFO.INFO()}>
  <div slot="header_content">
    {#if check_tournament_permission(user_info, tournament_permissions.edit_tournament, tournament.id, tournament.series_id)}
      <Button href="/{$page.params.lang}/tournaments/edit?id={tournament.id}">{$LL.TOURNAMENTS.EDIT_TOURNAMENT()}</Button>
      <Button href="/{$page.params.lang}/tournaments/edit_placements?id={tournament.id}">{$LL.TOURNAMENTS.EDIT_PLACEMENTS()}</Button>
    {/if}
    {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_roles, tournament.id, tournament.series_id)}
      <Button href="/{$page.params.lang}/tournaments/manage_roles?id={tournament.id}">{$LL.ROLES.MANAGE_ROLES()}</Button>
    {/if}
  </div>
  <div class="centered">
    {#if tournament.logo}
      <img src={tournament.logo} alt={tournament.name} />
    {/if}
    <div class="name">
      {tournament.name}
    </div>
    <div class="badges">
      <GameBadge game={tournament.game}/>
      <ModeBadge mode={tournament.mode}/>
      <TypeBadge is_squad={tournament.is_squad} teams_allowed={tournament.teams_allowed}/>
    </div>
    
  </div>
  <hr />
  <div class="wrapper">
    <div>
      <ul>
        <li>
          <b>{$LL.TOURNAMENTS.INFO.WHEN()}</b>
          {date_start.toLocaleString($locale, options)} - {date_end.toLocaleString($locale, options)}
        </li>
        {#if registration_deadline}
          <li><b>{$LL.TOURNAMENTS.INFO.REGISTRATION_DEADLINE()}</b> {registration_deadline.toLocaleString($locale, options)}</li>
        {/if}
        {#if tournament.location}
          <li><b>{$LL.TOURNAMENTS.INFO.LOCATION()}</b> {tournament.location}</li>
        {/if}
        <li><b>{$LL.COMMON.GAME()}:</b> {game_strings[tournament.game.toUpperCase()]()}</li>
        <li><b>{$LL.COMMON.MODE()}:</b> {mode_strings[tournament.mode.toUpperCase()]()}</li>
        <li><b>{$LL.TOURNAMENTS.INFO.REGISTRATION_FORMAT()}</b> {type}</li>
        {#if tournament.is_squad}
          {#if tournament.min_squad_size}
            <li><b>{$LL.TOURNAMENTS.INFO.MINIMUM_SQUAD_SIZE()}</b> {tournament.min_squad_size}</li>
          {/if}
          {#if tournament.max_squad_size}
            <li><b>{$LL.TOURNAMENTS.INFO.MAXIMUM_SQUAD_SIZE()}</b> {tournament.max_squad_size}</li>
          {/if}
        {/if}
        {#if tournament.series_name}
          <li><b>{$LL.TOURNAMENTS.INFO.PART_OF_SERIES()}</b> <a href="/{$page.params.lang}/tournaments/series/details?id={tournament.series_id}">{tournament.series_name}</a></li>
        {/if}
      </ul>
    </div>
  </div>
</Section>

<style>
  .centered {
    text-align: center;
    margin: auto auto auto auto;
  }
  .wrapper {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
  img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    max-width: 400px;
    max-height: 200px;
  }
  ul {
    padding-left: 0;
  }
  ul li {
    list-style-position: inside;
  }
  .name {
    font-size: 1.5em;
    font-weight: bold;
  }
  .badges {
    margin-top: 10px;
    margin-bottom: 10px;
  }
  hr {
    margin-top: 20px;
    margin-bottom: 20px;
  }
</style>
