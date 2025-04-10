<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import TournamentPlayerList from '$lib/components/tournaments/TournamentPlayerList.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import SoloTournamentFields from './SoloTournamentFields.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import ConfirmButton from '$lib/components/common/buttons/ConfirmButton.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import LL from '$i18n/i18n-svelte';

  export let tournament: Tournament;
  export let squads: TournamentSquad[];

  let all_toggle_on = false;
  let accept_dialog: Dialog;
  let curr_invite: TournamentSquad;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

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
      alert($LL.TOURNAMENTS.REGISTRATIONS.REGISTER_TOURNAMENT_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.REGISTER_TOURNAMENT_FAILED()}: ${result['title']}`);
    }
  }

  async function declineInvite(squad: TournamentSquad) {
    let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.DECLINE_INVITE_CONFIRM());
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
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.DECLINE_INVITE_FAILED()}: ${result['title']}`);
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
        <th>{$LL.COMMON.TAG()}</th>
      {/if}
      {#if tournament.squad_name_required}
        <th>{$LL.COMMON.NAME()}</th>
      {/if}
      <th>
        {$LL.TOURNAMENTS.REGISTRATIONS.PLAYERS()}
        <button class="show-players" on:click={toggle_all_players}>
          ({all_toggle_on ? $LL.TOURNAMENTS.REGISTRATIONS.HIDE_ALL_PLAYERS() : $LL.TOURNAMENTS.REGISTRATIONS.SHOW_ALL_PLAYERS()})
        </button>
      </th>
      <th>{$LL.INVITES.ACCEPT()}</th>
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
            {squad_data[squad.id].display_players ? $LL.COMMON.HIDE_BUTTON() : $LL.COMMON.SHOW_BUTTON()}
          </button></td
        >
        <td>
          <ConfirmButton on:click={() => inviteDialog(squad)}/>
          <CancelButton on:click={() => declineInvite(squad)}/>

        </td>
      </tr>
      {#if squad_data[squad.id].display_players}
        <tr class="inner">
          <td colspan="10">
            <TournamentPlayerList {tournament} players={squad.players} />
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</Table>

<Dialog bind:this={accept_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.ACCEPT_SQUAD_INVITE()}>
  <form method="POST" on:submit|preventDefault={acceptInvite}>
    {#if user_info.player}
      <SoloTournamentFields {tournament} friend_codes={user_info.player.friend_codes} />
      <br />
      <div>{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_ID}: {curr_invite?.id}</div>
      {#if tournament.squad_tag_required}
        <div>{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_TAG}: {curr_invite?.tag}</div>
      {/if}
      {#if tournament.squad_name_required}
        <div>{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_NAME}: {curr_invite?.name}</div>
      {/if}
      <br />
      <div>
        <Button type="submit">{$LL.INVITES.ACCEPT()}</Button>
        <Button type="button" on:click={accept_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
      </div>
    {/if}
    
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
