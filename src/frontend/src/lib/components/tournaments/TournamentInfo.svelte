<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import { locale } from '$i18n/i18n-svelte';
  import { series_permissions, permissions } from '$lib/util/util';
  import SeriesPermissionCheck from '../common/SeriesPermissionCheck.svelte';
  import PermissionCheck from '../common/PermissionCheck.svelte';
  import Section from '../common/Section.svelte';
  import LinkButton from '../common/LinkButton.svelte';
  import { page } from '$app/stores';

  export let tournament: Tournament;

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

<PermissionCheck permission={permissions.edit_tournament}>
  <Section header="Moderator">
    <div slot="header_content">
      <LinkButton href="/{$page.params.lang}/tournaments/mod/edit?id={tournament.id}">Edit Tournament</LinkButton>
    </div>
  </Section>
</PermissionCheck>

<Section header="Tournament Info">
  <div slot="header_content">
    <SeriesPermissionCheck series_id={tournament.series_id} permission={series_permissions.edit_tournament}>
      <LinkButton href="/{$page.params.lang}/tournaments/edit?id={tournament.id}">Edit Tournament</LinkButton>
    </SeriesPermissionCheck>
  </div>
  <div class="centered">
    {#if tournament.logo}
      <img src={tournament.logo} alt={tournament.tournament_name} />
    {/if}
    <h1>{tournament.tournament_name}</h1>
    {tournament.game} | {tournament.mode} | {tournament_type}
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
        <li><b>Game:</b> {tournament.game}</li>
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
</style>
