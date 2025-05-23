<script lang="ts">
  import type { RegistrationDetails } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import SquadTournamentFields from './SquadTournamentFields.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { check_registrations_open } from '$lib/util/util';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import TournamentPlayerList from '../TournamentPlayerList.svelte';
  import LL from '$i18n/i18n-svelte';
  import ManageSquadRosters from './ManageSquadRosters.svelte';
  import { game_fc_types } from '$lib/util/util';

  export let tournament: Tournament;
  export let registration: RegistrationDetails;

  let edit_squad_dialog: Dialog;
  let manage_rosters_dialog: ManageSquadRosters;

  let invite_player: PlayerInfo | null = null;
  let invite_as_bagger = false;

  let registered_players = registration.squad.players.filter((p) => !p.is_invite);
  let invited_players = registration.squad.players.filter((p) => p.is_invite);

  let working = false;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  async function invitePlayer(player: PlayerInfo | null) {
    if (!player) {
      return;
    }
    if (!registration.is_squad_captain) {
      return;
    }
    working = true;
    const payload = {
      registration_id: registration.squad.id,
      player_id: player.id,
      is_representative: false,
      is_bagger_clause: invite_as_bagger
    };
    const endpoint = `/api/tournaments/${tournament.id}/invitePlayer`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.INVITE_PLAYER_FAILED()}: ${result['title']}`);
    }
  }

  async function unregisterSquad() {
    if (!registration.is_squad_captain) {
      return;
    }
    let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_MY_SQUAD_CONFIRM());
    if (!conf) {
      return;
    }
    const payload = {
      registration_id: registration.squad.id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/unregisterSquad`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_FAILED()}: ${result['title']}`);
    }
  }

  async function editSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    working = true;
    const formData = new FormData(event.currentTarget);
    let squad_color = formData.get('squad_color');
    let squad_name = formData.get('squad_name');
    let squad_tag = formData.get('squad_tag');
    const payload = {
      registration_id: registration.squad.id,
      squad_color: Number(squad_color),
      squad_name: squad_name,
      squad_tag: squad_tag,
    };
    const endpoint = `/api/tournaments/${tournament.id}/editMySquad`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if tournament.is_squad}
  <div>{$LL.TOURNAMENTS.REGISTRATIONS.MY_SQUAD()}</div>
{:else}
  <div>{$LL.TOURNAMENTS.REGISTRATIONS.MY_REGISTRATION()}</div>
{/if}
<div>
  {#if tournament.squad_tag_required}
    <TagBadge tag={registration.squad.tag} color={registration.squad.color}/>
  {/if}
  {#if tournament.squad_name_required}
    {registration.squad.name}
  {/if}
</div>
{#if tournament.is_squad}
  <div>
    {$LL.TOURNAMENTS.REGISTRATIONS.PLAYER_COUNT({count: registered_players.length})}
  </div>
{/if}
<TournamentPlayerList {tournament} players={registered_players} {registration}/>

{#if invited_players.length > 0}
  <div>
    {$LL.TOURNAMENTS.REGISTRATIONS.INVITED_PLAYER_COUNT({count: invited_players.length})}
  </div>
  <TournamentPlayerList {tournament} players={invited_players} {registration} exclude_invites={false}/>
{/if}

{#if check_registrations_open(tournament) && registration.is_squad_captain}
  <!-- If registrations are open and our squad is not full and we are the squad captain -->
  {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true) &&
    (!tournament.max_squad_size || registration.squad.players.length < tournament.max_squad_size)}
    <div>
      <div><b>{$LL.TOURNAMENTS.REGISTRATIONS.INVITE_PLAYERS()}</b></div>
      <PlayerSearch
        bind:player={invite_player}
        fc_type={game_fc_types[tournament.game]}
        registration_id={tournament.team_members_only ? registration.squad.id : null}
      />
    </div>
    {#if invite_player}
      {#if tournament.bagger_clause_enabled}
        <div class="section">
          <label for="invite_as_bagger">
            {$LL.TOURNAMENTS.REGISTRATIONS.BAGGER_SELECT()}
          </label>
          <select name="invite_as_bagger" bind:value={invite_as_bagger}>
            <option value={false}>{$LL.COMMON.NO()}</option>
            <option value={true}>{$LL.COMMON.YES()}</option>
          </select>
        </div>
      {/if}
      <div class="section">
        <Button {working} on:click={() => invitePlayer(invite_player)}>{$LL.TOURNAMENTS.REGISTRATIONS.INVITE_PLAYER()}</Button>
      </div>
    {/if}
  {/if}
  <br />
  <div>
    {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true)}
      <Button on:click={edit_squad_dialog.open}>{$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD()}</Button>
    {/if}
    <Button on:click={unregisterSquad}>{$LL.TOURNAMENTS.REGISTRATIONS.UNREGISTER_SQUAD()}</Button>
    {#if tournament.teams_allowed}
      <Button on:click={() => manage_rosters_dialog.open(registration.squad)}>{$LL.TOURNAMENTS.REGISTRATIONS.MANAGE_ROSTERS()}</Button>
    {/if}
  </div>
{/if}

<Dialog bind:this={edit_squad_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD_REGISTRATION()}>
  <form method="POST" on:submit|preventDefault={editSquad}>
    <SquadTournamentFields {tournament} squad_color={registration.squad.color} squad_name={registration.squad.name} squad_tag={registration.squad.tag} />
    <br />
    <div>
      <Button {working} type="submit">{$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD()}</Button>
      <Button type="button" on:click={edit_squad_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
    </div>
  </form>
</Dialog>
<ManageSquadRosters bind:this={manage_rosters_dialog} {tournament}/>

<style>
  div.section {
    margin: 10px 0;
  }
</style>