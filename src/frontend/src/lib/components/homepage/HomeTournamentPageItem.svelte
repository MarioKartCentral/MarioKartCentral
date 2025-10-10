<script lang="ts">
  import { page } from '$app/stores';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import TypeBadge from '../badges/TypeBadge.svelte';
  import ModeBadge from '../badges/ModeBadge.svelte';
  import GameBadge from '../badges/GameBadge.svelte';
  import OrganizerBadge from '../badges/OrganizerBadge.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  export let tournament: TournamentListItem;
  import LL from '$i18n/i18n-svelte';

  let date_start = new Date(tournament.date_start * 1000);
  let date_end = new Date(tournament.date_end * 1000);

  let months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  // Appends leading 0 to single digit numbers
  const zeroPad = (num: number) => String(num).padStart(2, '0');
</script>

<div class="container mobile">
  <!-- tournament logo, name, and badges -->
  <div class="flex flex-col justify-evenly">
    <!-- logo and name -->
    <div class="flex gap-[5px] mobile-center">
      {#if tournament.logo}
        <div class="flex items-center w-[25px] h-[25px]">
          {#if tournament.series_id}
            <a href="/{$page.params.lang}/tournaments/series/details?id={tournament.series_id}">
              <img src={tournament.logo} alt={tournament.name} />
            </a>
          {:else}
            <a href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
              <img src={tournament.logo} alt={tournament.name} />
            </a>
          {/if}
        </div>
      {/if}
      <h3>
        <a class="text-lg font-bold p-1" href="/{$page.params.lang}/tournaments/details?id={tournament.id}"
          >{tournament.name}
        </a>
      </h3>
    </div>
    <!-- badges -->
    <div class="badges flex gap-[5px] flex-wrap mobile-center">
      <GameBadge game={tournament.game} style="font-size: 0.95rem;" />
      <ModeBadge mode={tournament.mode} style="font-size: 0.95rem;width:120px;" />
      <TypeBadge is_squad={tournament.is_squad} teams_allowed={tournament.teams_allowed} style="font-size: 0.95rem;" />
      <OrganizerBadge organizer={tournament.organizer} style="font-size: 0.95rem;" />
    </div>
  </div>
  <!-- date and register / view tournament button -->
  <div class="flex items-center mobile">
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
    </div>
    <div class="p-1 w-[210px] flex justify-center">
      {#if tournament.registrations_open}
        <Button size="sm" color="yellow" href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
          <span class="text-[1rem] font-[900]">{$LL.TOURNAMENTS.REGISTER_NOW()}</span>
        </Button>
      {:else}
        <Button size="sm" href="/{$page.params.lang}/tournaments/details?id={tournament.id}">
          <span class="text-[1rem] font-[900]">{$LL.TOURNAMENTS.VIEW_TOURNAMENT()}</span>
        </Button>
      {/if}
    </div>
  </div>
</div>

<style>
  .container {
    display: flex;
    justify-content: space-between;
    background-color: rgba(29, 33, 33, 0.8);
    padding: 12px 10px;
    margin: auto;
  }
  .container:nth-child(odd) {
    background-color: rgba(33, 39, 39, 0.8);
  }
  .badges {
    zoom: 80%;
  }
  img {
    max-width: 100%;
    max-height: 100%;
  }
  b {
    font-size: 1.2rem;
    font-weight: 900;
  }
  .dates {
    font-family: monospace;
  }
  @media (max-width: 768px) {
    .mobile {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .mobile-center {
      width: 100%;
      display: flex;
      justify-content: center;
    }
    .badges {
      margin-top: 10px;
    }
  }
</style>
