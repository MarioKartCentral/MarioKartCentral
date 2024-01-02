<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import TournamentPlayerList from '$lib/components/tournaments/TournamentPlayerList.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import SoloTournamentFields from './SoloTournamentFields.svelte';
  import type { FriendCode } from '$lib/types/friend-code';

  export let tournament: Tournament;
  export let squads: TournamentSquad[];
  export let friend_codes: FriendCode[];

  let all_toggle_on = false;
  let accept_dialog: Dialog;
  let curr_invite: TournamentSquad;

  // use this to store whether we should display players for each squad, as well as convert their timestamps to Dates
  let squad_data: { [id: number]: { display_players: boolean; date: Date } } = {};
  for (const squad of squads) {
    squad_data[squad.id] = { display_players: false, date: new Date(squad.timestamp * 1000) };
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

  function inviteDialog(squad: TournamentSquad) {
    curr_invite = squad;
    accept_dialog.open();
  }

  async function acceptInvite(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    if (!curr_invite) {
      return;
    }
    const formData = new FormData(event.currentTarget);
    let selected_fc_id = formData.get('selected_fc_id');
    let mii_name = formData.get('mii_name');
    let can_host = formData.get('can_host');
    const payload = {
      selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
      mii_name: mii_name,
      can_host: can_host === 'true',
      squad_id: curr_invite.id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/acceptInvite`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert('Successfully registered for the tournament!');
    } else {
      alert(`Registration failed: ${result['title']}`);
    }
  }

  async function declineInvite(squad: TournamentSquad) {
    let conf = window.confirm('Are you sure you would like to decline this invite?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: squad.id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/declineInvite`;
    console.log(payload);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`Declining invite failed: ${result['title']}`);
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
  <col class="accept" />
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
      <th>Accept/Decline</th>
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
          >{squad.players.filter((p) => !p.is_invite).length}
          <button class="show-players" on:click={() => toggle_show_players(squad.id)}>
            ({squad_data[squad.id].display_players ? 'hide' : 'show'})
          </button></td
        >
        <td>
          <button on:click={() => inviteDialog(squad)}>Accept</button>
          <button on:click={() => declineInvite(squad)}>Decline</button>
        </td>
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

<Dialog bind:this={accept_dialog} header="Accept squad invite">
  <form method="POST" on:submit|preventDefault={acceptInvite}>
    <SoloTournamentFields {tournament} {friend_codes} />
    <br />
    <div>Squad ID: {curr_invite?.id}</div>
    {#if tournament.squad_tag_required}
      <div>Squad Tag: {curr_invite?.tag}</div>
    {/if}
    {#if tournament.squad_name_required}
      <div>Squad Name: {curr_invite?.name}</div>
    {/if}
    <br />
    <div>
      <button type="submit">Accept</button>
      <button type="button" on:click={accept_dialog.close}>Cancel</button>
    </div>
  </form>
</Dialog>

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
  col.accept {
    width: 30%;
  }
</style>
