<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import { locale } from '$i18n/i18n-svelte';
  import { slide } from 'svelte/transition';
  import TournamentPlayerList from './TournamentPlayerList.svelte';
  import Table from '$lib/components/common/Table.svelte';

  export let tournament: Tournament;
  export let squads: TournamentSquad[];

  let all_toggle_on = false;

  // use this to store whether we should display players for each squad, as well as convert their timestamps to Dates
  let squad_data: { [id: number]: { display_players: boolean; date: Date } } = {};
  for (const squad of squads) {
    squad_data[squad.id] = { display_players: false, date: new Date(squad.timestamp * 1000) };
  }

  function is_squad_eligible(squad: TournamentSquad) {
    if (tournament.min_squad_size === null) {
      return 'Yes';
    }
    return squad.players.length >= tournament.min_squad_size ? 'Yes' : 'No';
  }

  function toggle_show_players(squad_id: number) {
    squad_data[squad_id].display_players = !squad_data[squad_id].display_players;
  }

  function toggle_all_players() {
    all_toggle_on = !all_toggle_on;
    for (const squad of squads) {
      squad_data[squad.id].display_players = all_toggle_on;
    }
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };
</script>

<Table>
  <col class="id" />
  {#if tournament.squad_tag_required}
    <col class="tag" />
  {/if}
  {#if tournament.squad_name_required}
    <col class="name" />
  {/if}
  <col class="players" />
  <col class="eligible" />
  <col class="date" />
  <thead>
    <tr>
      <th>ID</th>
      {#if tournament.squad_tag_required}
        <th>Tag</th>
      {/if}
      {#if tournament.squad_name_required}
        <th>Name</th>
      {/if}
      <th>
        Players
        <button class="show-players" on:click={toggle_all_players}>
          ({all_toggle_on ? 'hide all' : 'show all'})
        </button>
      </th>
      <th>Eligible?</th>
      <th>Registration Date</th>
    </tr>
  </thead>
  <tbody>
    {#each squads as squad, i}
      <tr class="row-{i % 2}">
        <td>{squad.id}</td>
        {#if tournament.squad_tag_required}
          <td>{squad.tag}</td>
        {/if}
        {#if tournament.squad_name_required}
          <td>{squad.name}</td>
        {/if}
        <td
          >{squad.players.length}
          <button class="show-players" on:click={() => toggle_show_players(squad.id)}>
            ({squad_data[squad.id].display_players ? 'hide' : 'show'})
          </button></td
        >
        <td>{is_squad_eligible(squad)}</td>
        <td>{squad_data[squad.id].date.toLocaleString($locale, options)}</td>
      </tr>
      {#if squad_data[squad.id].display_players}
        <tr class="row-{i % 2}">
          <td colspan="10">
            <TournamentPlayerList {tournament} players={squad.players} />
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</Table>

<style>
  button.show-players {
    background-color: transparent;
    border: none;
    color: white;
    cursor: pointer;
  }
  col.id {
    width: 10%;
  }
  col.tag {
    width: 15%;
  }
  col.name {
    width: 30%;
  }
  col.players {
    width: 15%;
  }
  col.eligible {
    width: 10%;
  }
  col.date {
    width: 20%;
  }
</style>
