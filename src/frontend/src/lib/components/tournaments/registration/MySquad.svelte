<script lang="ts">
  import type { TournamentSquad } from '$lib/types/tournament-squad';
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
  import type { TournamentPlayer } from '$lib/types/tournament-player';

  export let tournament: Tournament;
  export let squad: TournamentSquad;
  export let my_player: TournamentPlayer;

  let edit_squad_dialog: Dialog;

  let invite_player: PlayerInfo | null = null;
  let invite_as_bagger = false;

  let registered_players = squad.players.filter((p) => !p.is_invite);
  let invited_players = squad.players.filter((p) => p.is_invite);

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  async function invitePlayer(player: PlayerInfo | null) {
    if (!player) {
      return;
    }

    if (!my_player.is_squad_captain) {
      return;
    }
    const payload = {
      squad_id: my_player.squad_id,
      player_id: player.id,
      is_representative: false,
      is_bagger_clause: invite_as_bagger
    };
    const endpoint = `/api/tournaments/${tournament.id}/invitePlayer`;
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
      alert(`Invitation failed: ${result['title']}`);
    }
  }

  async function unregisterSquad() {
    if (!my_player.is_squad_captain) {
      return;
    }
    let conf = window.confirm('Are you sure you would like to withdraw your squad from this tournament?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: my_player.squad_id,
    };
    console.log(payload);
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
      alert(`Failed to unregister: ${result['title']}`);
    }
  }

  async function editSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const formData = new FormData(event.currentTarget);
    let squad_color = formData.get('squad_color');
    let squad_name = formData.get('squad_name');
    let squad_tag = formData.get('squad_tag');
    const payload = {
      squad_id: squad.id,
      squad_color: Number(squad_color),
      squad_name: squad_name,
      squad_tag: squad_tag,
    };
    const endpoint = `/api/tournaments/${tournament.id}/editMySquad`;
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
      alert(`Editing squad failed: ${result['title']}`);
    }
  }
</script>

<div>My squad</div>

<div>
  {#if tournament.squad_tag_required}
    <TagBadge tag={squad.tag} color={squad.color}/>
  {/if}
  {#if tournament.squad_name_required}
    {squad.name}
  {/if}
</div>
<div>{registered_players.length} players</div>
<TournamentPlayerList {tournament} players={registered_players} {my_player}/>

{#if invited_players.length > 0}
  <div>{invited_players.length} invited players</div>
  <TournamentPlayerList {tournament} players={invited_players} {my_player} exclude_invites={false}/>
{/if}

{#if check_registrations_open(tournament) && my_player.is_squad_captain}
  <!-- If registrations are open and our squad is not full and we are the squad captain -->
  {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true) &&
    (!tournament.max_squad_size || squad.players.length < tournament.max_squad_size)}
    <div class="section">
      <div><b>Invite players</b></div>
      <PlayerSearch
        bind:player={invite_player}
        game={tournament.game}
        squad_id={tournament.team_members_only ? my_player.squad_id : null}
      />
    </div>
    {#if invite_player}
      {#if tournament.bagger_clause_enabled}
        <div class="section">
          <label for="invite_as_bagger">
            Bagger?
          </label>
          <select name="invite_as_bagger" bind:value={invite_as_bagger}>
            <option value={false}>No</option>
            <option value={true}>Yes</option>
          </select>
        </div>
      {/if}
      <div class="section">
        <Button on:click={() => invitePlayer(invite_player)}>Invite Player</Button>
      </div>
    {/if}
  {/if}
  <br />
  <div>
    {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true)}
      <Button on:click={edit_squad_dialog.open}>Edit Squad</Button>
    {/if}
    <Button on:click={unregisterSquad}>Unregister Squad</Button>
  </div>
{/if}

<Dialog bind:this={edit_squad_dialog} header="Edit Squad Registration">
  <form method="POST" on:submit|preventDefault={editSquad}>
    <SquadTournamentFields {tournament} squad_color={squad.color} squad_name={squad.name} squad_tag={squad.tag} />
    <br />
    <div>
      <Button type="submit">Edit Squad</Button>
      <Button type="button" on:click={edit_squad_dialog.close}>Cancel</Button>
    </div>
  </form>
</Dialog>

<style>
  div.section {
    margin: 10px 0;
  }
</style>