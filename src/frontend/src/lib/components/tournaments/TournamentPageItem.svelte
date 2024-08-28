<script lang="ts">
  import { page } from '$app/stores';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import TypeBadge from '../badges/TypeBadge.svelte';
  import ModeBadge from '../badges/ModeBadge.svelte';
  import GameBadge from '../badges/GameBadge.svelte';
  export let tournament: TournamentListItem;

  let date_start = new Date(tournament.date_start * 1000);
  let date_end = new Date(tournament.date_end * 1000);

  $: tournament_type = tournament.is_squad ? (tournament.teams_allowed ? 'Team' : 'Squad') : 'Solo';
  let months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
</script>

<div class="container">
  <!-- <div>{tournament.id}</div> -->
  <div class="name">
    <h3><a href="/{$page.params.lang}/tournaments/details?id={tournament.id}">{tournament.tournament_name}</a></h3>
  </div>
  <GameBadge game={tournament.game}/>
  <ModeBadge mode={tournament.mode}/>
  <TypeBadge type={tournament_type}/>
  <div>{months[date_start.getMonth()]} {date_start.getDate()}-{months[date_end.getMonth()]} {date_end.getDate()}</div>
  {#if tournament.logo != null}
    <div><img src={tournament.logo} alt={tournament.tournament_name} /></div>
  {/if}
  {#if tournament.series_id != null}
    <div><a href="/{$page.params.lang}/tournaments/series/details?id={tournament.series_id}">Series {tournament.series_id} - {tournament.series_name}</a></div>
    <div>{tournament.series_description}</div>
  {/if}
</div>

<style>
  .container {
    display: grid;
    background-color: rgba(24, 82, 28, 0.8);
    padding-top: 10px;
    padding-bottom: 10px;
    margin: 10px auto 10px auto;
  }
  .name {
    display: inline-block;
  }
  img {
    max-width: 400px;
    max-height: 200px;
  }
</style>
