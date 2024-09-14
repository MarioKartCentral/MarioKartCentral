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

  export let tournament: Tournament;
  export let squads: TournamentSquad[];
  export let is_privileged = false;

  let edit_squad_dialog: EditSquadDialog;

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
    return squad.players.filter(p => !p.is_invite).length >= tournament.min_squad_size ? 'Yes' : 'No';
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

  async function unregisterSquad(squad: TournamentSquad) {
    let conf = window.confirm('Are you sure you would like to remove this squad from this tournament?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: squad.id,
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
      alert(`Failed to unregister: ${result['title']}`);
    }
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
    <col class="actions"/>
  {/if}
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
      <th class="mobile-hide">Eligible?</th>
      <th class="mobile-hide">Registration Date</th>
      {#if is_privileged}
        <th>Actions</th>
      {/if}
    </tr>
  </thead>
  <tbody>
    {#each squads as squad, i}
      <tr class="row-{i % 2}">
        <td>{squad.id}</td>
        {#if tournament.squad_tag_required}
          <td>
            <TagBadge tag={squad.tag} color={squad.color}/>
          </td>
        {/if}
        {#if tournament.squad_name_required}
          <td>{squad.name}</td>
        {/if}
        <td
          >{squad.players.filter((p) => !p.is_invite).length}
          <button class="show-players" on:click={() => toggle_show_players(squad.id)}>
            ({squad_data[squad.id].display_players ? 'hide' : 'show'})
          </button></td
        >
        <td class="mobile-hide">{is_squad_eligible(squad)}</td>
        <td class="mobile-hide">{squad_data[squad.id].date.toLocaleString($locale, options)}</td>
        {#if is_privileged}
          <td>
            <ChevronDownSolid class="cursor-pointer"/>
            <Dropdown>
              <DropdownItem on:click={() => edit_squad_dialog.open(squad)}>Edit</DropdownItem>
              <DropdownItem on:click={() => unregisterSquad(squad)}>Remove</DropdownItem>
            </Dropdown>
          </td>
        {/if}
      </tr>
      {#if squad_data[squad.id].display_players}
        <tr class="row-{i % 2}">
          <td colspan="10">
            <TournamentPlayerList {tournament} players={squad.players} {is_privileged}/>
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</Table>

<EditSquadDialog bind:this={edit_squad_dialog} {tournament} {is_privileged}/>

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
