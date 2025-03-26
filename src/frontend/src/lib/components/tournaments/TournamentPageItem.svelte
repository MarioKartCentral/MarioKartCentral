<script lang="ts">
  import { page } from '$app/stores';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import TypeBadge from '../badges/TypeBadge.svelte';
  import ModeBadge from '../badges/ModeBadge.svelte';
  import GameBadge from '../badges/GameBadge.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  export let tournament: TournamentListItem;
  import LL from '$i18n/i18n-svelte';

  let date_start = new Date(tournament.date_start * 1000);
  let date_end = new Date(tournament.date_end * 1000);

  let months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  // Appends leading 0 to single digit numbers
  const zeroPad = (num: number) => String(num).padStart(2, '0');
</script>

<div class="container {!tournament.is_viewable || !tournament.is_public ? 'tournament-hidden' : ''}">
  <div class="grid-container">
    <!-- Informational Section -->
    <div class="information flex flex-col align-middle items-center justify-center text-center">
      <div class="italic">
        {#if !tournament.is_viewable}
          {$LL.TOURNAMENTS.UNPUBLISHED()}
        {:else if !tournament.is_public}
          {$LL.TOURNAMENTS.HIDDEN_FROM_TOURNAMENT_PAGE()}
        {/if}
      </div>
      <div class="name">
        <h3>
          <a
            class="text-lg font-bold hover:text-emerald-400 p-1"
            href="/{$page.params.lang}/tournaments/details?id={tournament.id}"
            >{tournament.name}
          </a>
        </h3>
      </div>
      <div class="dates flex flex-row">
        <div class="start-date flex flex-col text-center p-1">
          <b>
            {months[date_start.getMonth()].toUpperCase()}
          </b>
          <b>
            {zeroPad(date_start.getDate())}
          </b>
        </div>
        <div class="dash flex flex-row text-center align-middle p-1 mt-3">
          <b>–</b>
        </div>
        <div class="end-date flex flex-col text-center p-1">
          <b>
            {months[date_end.getMonth()].toUpperCase()}
          </b>
          <b>
            {zeroPad(date_end.getDate())}
          </b>
        </div>
        <!-- Badges -->
        <div class="badges flex flex-col p-1">
          <GameBadge game={tournament.game} />
          <ModeBadge mode={tournament.mode} />
          <TypeBadge is_squad={tournament.is_squad} teams_allowed={tournament.teams_allowed}/>
        </div>
      </div>
    </div>

    <!-- Logo Section -->
    <div class="logo flex flex-col justify-center items-center text-center">
      {#if tournament.logo != null}
        <div class="font-bold">
          {#if tournament.series_name != null}
            <a href="/{$page.params.lang}/tournaments/series/details?id={tournament.series_id}">
              {tournament.series_name}
            </a>
          {/if}
        </div>
        {#if tournament.series_id}
          <a href="/{$page.params.lang}/tournaments/series/details?id={tournament.series_id}">
            <img src={tournament.logo} alt={tournament.name} />
          </a>
        {:else}
          <a href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
            <img src={tournament.logo} alt={tournament.name} />
          </a>
        {/if}
        
      {/if}
    </div>

    <!-- Description & CTA section -->
    <div class="cta flex flex-col justify-center">
      <div class="description">
        {#if tournament.series_id != null}
          <div class="text-gray-300 p-1">{tournament.series_short_description}</div>
        {/if}
      </div>
      {#if tournament.registrations_open}
        <div class="register-button p-1">
          <Button size="sm" color="yellow" href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
            <b>{$LL.TOURNAMENTS.REGISTER_NOW()}</b>
          </Button>
        </div>
      {:else}
        <div class="view-tournament-button p-1">
          <Button size="sm" href="/{$page.params.lang}/tournaments/details?id={tournament.id}"
            ><b>{$LL.TOURNAMENTS.VIEW_TOURNAMENT()}</b></Button
          >
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .tournament-hidden {
    opacity: 0.5;
  }
  .container {
    background-color: rgba(29, 33, 33, 0.8);
    padding-top: 10px;
    padding-bottom: 10px;
    margin: 10px auto 10px auto;
  }
  .container:nth-child(odd) {
    background-color: rgba(33, 39, 39, 0.8);
  }
  img {
    max-width: 76px;
    max-height: 76px;
  }
  b {
    font-size: 1.2rem;
    font-weight: 900;
  }
  .dates {
    font-family: monospace;
  }
  .grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
  .description {
    font-size: 0.9rem;
  }
  @media (max-width: 768px) {
    .grid-container {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .description {
      display: none;
    }
    .cta {
      text-align: center;
    }
  }
</style>
