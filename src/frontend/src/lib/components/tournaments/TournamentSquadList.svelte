<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import { locale } from '$i18n/i18n-svelte';
  import TournamentPlayerList from './TournamentPlayerList.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '../common/Dropdown.svelte';
  import DropdownItem from '../common/DropdownItem.svelte';
  import EditSquadDialog from './registration/EditSquadDialog.svelte';
  import AddPlayerToSquad from './registration/AddPlayerToSquad.svelte';
  import LL from '$i18n/i18n-svelte';
  import ManageSquadRosters from './registration/ManageSquadRosters.svelte';
  import { page } from '$app/stores';

  export let tournament: Tournament;
  export let squads: TournamentSquad[];
  export let is_privileged = false;

  export let show_all = false;
  let display_limit = 12;
  let sorted_by = 'register-date';

  let edit_squad_dialog: EditSquadDialog;
  let add_player_dialog: AddPlayerToSquad;
  let manage_rosters_dialog: ManageSquadRosters;

  let all_toggle_on = false;

  // use this to store whether we should display players for each squad, as well as convert their timestamps to Dates
  let squad_data: { [id: number]: { display_players: boolean; date: Date } } = {};
  for (const squad of squads) {
    squad_data[squad.id] = { display_players: false, date: new Date(squad.timestamp * 1000) };
  }

  function is_squad_eligible(squad: TournamentSquad) {
    if (tournament.min_squad_size !== null) {
      if (squad.players.filter((p) => !p.is_invite).length < tournament.min_squad_size) {
        return false;
      }
    }
    if (tournament.min_players_checkin !== null) {
      if (squad.players.filter((p) => p.is_checked_in).length < tournament.min_players_checkin) {
        return false;
      }
    }
    return true;
  }

  function toggle_show_players(registration_id: number) {
    squad_data[registration_id].display_players = !squad_data[registration_id].display_players;
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

  async function unregisterSquad(squad: TournamentSquad) {
    let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_SQUAD_CONFIRM());
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: squad.id,
    };
    console.log(payload);
    const endpoint = `/api/tournaments/${tournament.id}/forceUnregisterSquad`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_SQUAD_FAILED()}: ${result['title']}`);
    }
  }

  function sortSquadsByName() {
    if (sorted_by !== 'name') {
      squads.sort((a, b) => String(a.name).toLowerCase().localeCompare(String(b.name).toLowerCase()));
    }
    // sort in reverse if already sorted by name
    else {
      squads.reverse();
    }
    squads = squads;
    sorted_by = 'name';
  }

  function sortSquadsByRegistrationDate() {
    if (sorted_by !== 'register-date') {
      squads.sort((a, b) => a.timestamp - b.timestamp);
    } else {
      squads.reverse();
    }
    squads = squads;
    sorted_by = 'register-date';
  }
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
  <col class="eligible mobile-hide" />
  <col class="date mobile-hide" />
  {#if is_privileged}
    <col class="actions" />
  {/if}
  <thead>
    <tr>
      <th>ID</th>
      {#if tournament.squad_tag_required}
        <th>{$LL.COMMON.TAG()}</th>
      {/if}
      {#if tournament.squad_name_required}
        <th>
          <button class="show-players" on:click={sortSquadsByName}>
            {$LL.COMMON.NAME()}
          </button>
        </th>
      {/if}
      <th>
        {$LL.TOURNAMENTS.REGISTRATIONS.PLAYERS()}
        <button class="show-players" on:click={toggle_all_players}>
          {all_toggle_on
            ? $LL.TOURNAMENTS.REGISTRATIONS.HIDE_ALL_PLAYERS()
            : $LL.TOURNAMENTS.REGISTRATIONS.SHOW_ALL_PLAYERS()}
        </button>
      </th>
      <th class="mobile-hide">{$LL.TOURNAMENTS.REGISTRATIONS.ELIGIBLE()}</th>
      <th class="mobile-hide">
        <button class="show-players" on:click={sortSquadsByRegistrationDate}>
          {$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATION_DATE()}
        </button>
      </th>
      {#if is_privileged}
        <th />
      {/if}
    </tr>
  </thead>
  <tbody>
    {#key [squads, show_all]}
      {#each show_all ? squads : squads.slice(0, display_limit) as squad, i (squad.id)}
        <tr class="row-{i % 2}">
          <td>{squad.id}</td>
          {#if tournament.squad_tag_required}
            <td>
              <TagBadge tag={squad.tag} color={squad.color} />
            </td>
          {/if}
          {#if tournament.squad_name_required}
            <td>
              {#if squad.rosters.length}
                <a href="/{$page.params.lang}/registry/teams/profile?id={squad.rosters[0].team_id}">
                  {squad.name}
                </a>
              {:else}
                {squad.name}
              {/if}
            </td>
          {/if}
          <td
            >{squad.players.filter((p) => !p.is_invite).length}
            <button class="show-players" on:click={() => toggle_show_players(squad.id)}>
              {squad_data[squad.id].display_players ? $LL.COMMON.HIDE_BUTTON() : $LL.COMMON.SHOW_BUTTON()}
            </button></td
          >
          <td class="mobile-hide">
            {is_squad_eligible(squad) ? $LL.COMMON.YES() : $LL.COMMON.NO()}
          </td>
          <td class="mobile-hide">{squad_data[squad.id].date.toLocaleString($locale, options)}</td>
          {#if is_privileged}
            <td>
              <ChevronDownSolid class="cursor-pointer" />
              <Dropdown>
                {#if !tournament.max_squad_size || squad.players.length < tournament.max_squad_size}
                  <DropdownItem on:click={() => add_player_dialog.open(squad)}
                    >{$LL.TOURNAMENTS.REGISTRATIONS.ADD_PLAYER()}</DropdownItem
                  >
                {/if}
                <DropdownItem on:click={() => edit_squad_dialog.open(squad)}>{$LL.COMMON.EDIT()}</DropdownItem>
                <DropdownItem on:click={() => unregisterSquad(squad)}
                  >{$LL.TOURNAMENTS.REGISTRATIONS.REMOVE()}</DropdownItem
                >
                {#if tournament.teams_allowed}
                  <DropdownItem on:click={() => manage_rosters_dialog.open(squad)}
                    >{$LL.TOURNAMENTS.REGISTRATIONS.MANAGE_ROSTERS()}</DropdownItem
                  >
                {/if}
              </Dropdown>
            </td>
          {/if}
        </tr>
        {#if squad_data[squad.id].display_players}
          <tr class="inner">
            <td colspan="10">
              <TournamentPlayerList {tournament} players={squad.players} {is_privileged} />
            </td>
          </tr>
        {/if}
      {/each}
    {/key}
  </tbody>
</Table>

<AddPlayerToSquad bind:this={add_player_dialog} {tournament} />
<EditSquadDialog bind:this={edit_squad_dialog} {tournament} is_privileged={true} />
<ManageSquadRosters bind:this={manage_rosters_dialog} {tournament} is_privileged={true} />

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
    width: 10%;
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
    width: 15%;
  }
  col.actions {
    width: 10%;
  }
</style>
