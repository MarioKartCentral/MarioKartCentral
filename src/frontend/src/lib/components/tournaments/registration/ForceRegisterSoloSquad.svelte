<script lang="ts">
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { Tournament } from '$lib/types/tournament';
  import SoloTournamentFields from './SoloTournamentFields.svelte';
  import SquadTournamentFields from './SquadTournamentFields.svelte';
  import PlayerSearch from '$lib/components/common/search/PlayerSearch.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TournamentStaffFields from './TournamentStaffFields.svelte';
  import CreateShadowPlayerDialog from '$lib/components/registry/players/CreateShadowPlayerDialog.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import { game_fc_types } from '$lib/util/util';

  export let tournament: Tournament;
  let player: PlayerInfo | null;
  let working = false;

  let shadow_dialog: CreateShadowPlayerDialog;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  async function registerSolo(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    if (!player) return;
    working = true;
    const formData = new FormData(event.currentTarget);
    let selected_fc_id = formData.get('selected_fc_id');
    let mii_name = formData.get('mii_name');
    let can_host = formData.get('can_host');
    let is_checked_in = formData.get('is_checked_in');
    let is_approved = formData.get('is_approved');
    const payload = {
      player_id: player.id,
      selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
      mii_name: mii_name,
      can_host: can_host === 'true',
      is_checked_in: is_checked_in === 'true',
      is_approved: is_approved === 'true',
    };
    const endpoint = `/api/tournaments/${tournament.id}/forceRegister`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TOURNAMENTS.REGISTRATIONS.MANUAL_REGISTRATION_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.MANUAL_REGISTRATION_FAILED()}: ${result['title']}`);
    }
  }
  async function registerSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    if (!player) return;
    working = true;
    const formData = new FormData(event.currentTarget);
    let squad_color = formData.get('squad_color');
    let squad_name = formData.get('squad_name');
    let squad_tag = formData.get('squad_tag');
    let selected_fc_id = formData.get('selected_fc_id');
    let mii_name = formData.get('mii_name');
    let can_host = formData.get('can_host');
    let is_bagger_clause = formData.get('is_bagger_clause');
    let is_checked_in = formData.get('is_checked_in');
    let is_approved = formData.get('is_approved');
    const payload = {
      player_id: player.id,
      squad_color: Number(squad_color),
      squad_name: squad_name,
      squad_tag: squad_tag,
      selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
      mii_name: mii_name,
      can_host: can_host === 'true',
      is_bagger_clause: is_bagger_clause === 'true',
      is_checked_in: is_checked_in === 'true',
      is_approved: is_approved === 'true',
    };
    const endpoint = `/api/tournaments/${tournament.id}/forceCreateSquad`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TOURNAMENTS.REGISTRATIONS.MANUAL_REGISTRATION_SUCCESS());
    } else {
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.MANUAL_REGISTRATION_FAILED()}: ${result['title']}`);
    }
  }
</script>

<div class="manual-register">
  <div class="register_player_text">
    {#if tournament.is_squad}
      {$LL.TOURNAMENTS.REGISTRATIONS.MANUALLY_REGISTER_SQUAD()}
    {:else}
      {$LL.TOURNAMENTS.REGISTRATIONS.MANUALLY_REGISTER_PLAYER()}
    {/if}
    {#if check_permission(user_info, permissions.manage_shadow_players)}
      <Button on:click={shadow_dialog.open}>{$LL.PLAYERS.SHADOW_PLAYERS.CREATE_SHADOW_PLAYER()}</Button>
    {/if}
  </div>
  <PlayerSearch
    bind:player
    showFriendCode
    fcType={game_fc_types[tournament.game]}
    showId
    includeShadowPlayers
    showProfileLink
  />
  {#if player}
    <form method="POST" on:submit|preventDefault={tournament.is_squad ? registerSquad : registerSolo}>
      <SquadTournamentFields {tournament} />
      <SoloTournamentFields {tournament} friend_codes={player.friend_codes} />
      <TournamentStaffFields {tournament} />
      <Button {working} type="submit">{$LL.TOURNAMENTS.REGISTRATIONS.REGISTER()}</Button>
    </form>
  {/if}
</div>

<CreateShadowPlayerDialog bind:this={shadow_dialog} />

<style>
  .manual-register {
    margin-top: 20px;
  }
  .register_player_text {
    margin-top: 10px;
    margin-bottom: 10px;
  }
</style>
