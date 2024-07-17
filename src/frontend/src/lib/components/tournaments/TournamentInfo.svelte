<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import { locale } from '$i18n/i18n-svelte';
  import { valid_games } from '$lib/util/util';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import Section from '../common/Section.svelte';
  import Button from '../common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import GameBadge from '../badges/GameBadge.svelte';
  import TypeBadge from '../badges/TypeBadge.svelte';
  import ModeBadge from '../badges/ModeBadge.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';

  export let tournament: Tournament;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  $: tournament_type = tournament.is_squad ? (tournament.teams_allowed ? 'Team' : 'Squad') : 'Solo';
  let date_start = new Date(tournament.date_start * 1000);
  let date_end = new Date(tournament.date_end * 1000);
  let registration_deadline = tournament.registration_deadline
    ? new Date(tournament.registration_deadline * 1000)
    : null;
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };
</script>

<Section header="Tournament Info">
  <div slot="header_content">
    {#if check_tournament_permission(user_info, tournament_permissions.edit_tournament, tournament.id, tournament.series_id)}
      <Button href="/{$page.params.lang}/tournaments/edit?id={tournament.id}">Edit Tournament</Button>
      <Button href="/{$page.params.lang}/tournaments/edit_placements?id={tournament.id}">Edit Placements</Button>
    {/if}
  </div>
  <div class="centered">
    {#if tournament.logo}
      <img src={tournament.logo} alt={tournament.tournament_name} />
    {/if}
    <div class="name">
      {tournament.tournament_name}
    </div>
    <div class="badges">
      <GameBadge game={tournament.game}/>
      <ModeBadge mode={tournament.mode}/>
      <TypeBadge type={tournament_type}/>
    </div>
    
  </div>
  <hr />
  <div class="wrapper">
    <div>
      <ul>
        <li>
          <b>When:</b>
          {date_start.toLocaleString($locale, options)} - {date_end.toLocaleString($locale, options)}
        </li>
        {#if registration_deadline}
          <li><b>Registration Deadline:</b> {registration_deadline.toLocaleString($locale, options)}</li>
        {/if}
        <li><b>Game:</b> {valid_games[tournament.game]}</li>
        <li><b>Mode:</b> {tournament.mode}</li>
        <li><b>Registration Format:</b> {tournament_type}</li>
        {#if tournament.is_squad}
          {#if tournament.min_squad_size}
            <li><b>Minimum Squad Size:</b> {tournament.min_squad_size}</li>
          {/if}
          {#if tournament.max_squad_size}
            <li><b>Maximum Squad Size:</b> {tournament.max_squad_size}</li>
          {/if}
        {/if}
        {#if tournament.series_name}
          <li><b>Series:</b> {tournament.series_name}</li>
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
