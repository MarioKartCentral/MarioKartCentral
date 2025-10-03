<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { BanListData, BanInfoDetailed } from '$lib/types/ban-info';
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Dialog from '$lib/components/common/Dialog.svelte';
  import PlayerProfile from '$lib/components/registry/players/PlayerProfile.svelte';
  import PlayerProfileBan from '$lib/components/registry/players/PlayerProfileBan.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import PlayerNotes from '$lib/components/registry/players/PlayerNotes.svelte';
  import EditPlayerNotes from '$lib/components/registry/players/EditPlayerNotes.svelte';
  import ClaimPlayer from '$lib/components/registry/players/ClaimPlayer.svelte';
  import PlayerTournamentHistory from '$lib/components/registry/players/PlayerTournamentHistory.svelte';
  import PlayerRegistrationHistory from '$lib/components/registry/players/PlayerRegistrationHistory.svelte';
  import PlayerAltFlags from '$lib/components/moderator/PlayerAltFlags.svelte';
  import PlayerLogins from '$lib/components/moderator/PlayerLogins.svelte';
  import PlayerIpDialog from '$lib/components/moderator/PlayerIPDialog.svelte';

  let user_info: UserInfo;
  let banDialog: Dialog;
  let editBanDialog: Dialog;
  let playerNotesDialog: Dialog;
  let altDialog: PlayerAltFlags;
  let loginDialog: PlayerLogins;
  let ipDialog: PlayerIpDialog;
  let show_notes = false;

  user.subscribe((value) => {
    user_info = value;
  });

  let id = 0;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  let player_found = true;
  let player: PlayerInfo;
  let banInfo: BanInfoDetailed | null = null;
  let resetPlayerNotes = false;

  $: player_name = player ? player.name : 'Registry';

  const mod_permissions = [
    permissions.ban_player,
    permissions.edit_player,
    permissions.view_alt_flags,
    permissions.edit_user,
  ];

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/registry/players/${id}`);
    if (res.status != 200) {
      player_found = false;
      return;
    }
    const body: PlayerInfo = await res.json();
    player = body;

    if (player.ban_info) {
      // fetch detailed ban info. api will only return successfully if the user is a mod
      const res2 = await fetch(`/api/registry/players/bans?player_id=${player.id}`);
      if (res2.status === 200) {
        const data: BanListData = await res2.json();
        if (data.ban_count === 1) banInfo = data.ban_list[0];
      }
    }
  });

  function openEditPlayerNotesDialog() {
    resetPlayerNotes = !resetPlayerNotes;
    playerNotesDialog.open();
  }
  function closeEditPlayerNotesDialog() {
    resetPlayerNotes = !resetPlayerNotes;
    playerNotesDialog.close();
  }

  async function sendPasswordReset() {
    let conf = window.confirm($LL.PLAYERS.PROFILE.SEND_PASSWORD_RESET_CONFIRM());
    if (!conf) return;
    const payload = {
      player_id: player.id,
    };
    const endpoint = '/api/user/send_player_password_reset';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      alert($LL.PLAYERS.PROFILE.SEND_PASSWORD_RESET_SUCCESS());
    } else {
      alert(`${$LL.PLAYERS.PROFILE.SEND_PASSWORD_RESET_FAILED()}: ${result['title']}`);
    }
  }
</script>

<svelte:head>
  <title>{player_name} | MKCentral</title>
</svelte:head>

{#if player}
  {#if player.ban_info}
    <PlayerProfileBan ban_info={player.ban_info} />
  {/if}

  {#if mod_permissions.some((p) => check_permission(user_info, p))}
    <Section header={$LL.NAVBAR.MODERATOR()}>
      <div slot="header_content">
        {#if check_permission(user_info, permissions.ban_player)}
          <Dialog bind:this={banDialog} header={$LL.PLAYER_BAN.BAN_PLAYER()}>
            <BanPlayerForm playerId={player.id} playerName={player.name} handleCancel={() => banDialog.close()} />
          </Dialog>
          <Dialog bind:this={editBanDialog} header={$LL.PLAYER_BAN.VIEW_EDIT_BAN()}>
            {#if banInfo}
              <ViewEditBan {banInfo} />
            {/if}
          </Dialog>
          {#if !player.is_banned}
            <Button on:click={banDialog.open}>{$LL.PLAYER_BAN.BAN_PLAYER()}</Button>
          {:else}
            <Button on:click={editBanDialog.open}>{$LL.PLAYER_BAN.VIEW_EDIT_BAN()}</Button>
          {/if}
        {/if}
        {#if check_permission(user_info, permissions.edit_player)}
          <Dialog
            bind:this={playerNotesDialog}
            on:close={() => (resetPlayerNotes = !resetPlayerNotes)}
            header={$LL.PLAYERS.PROFILE.EDIT_PLAYER_NOTES()}
          >
            {#key resetPlayerNotes}
              <EditPlayerNotes
                playerId={player.id}
                notes={player.notes?.notes || ''}
                on:cancel={closeEditPlayerNotesDialog}
              />
            {/key}
          </Dialog>
          <Button href="/{$page.params.lang}/registry/players/mod-edit-profile?id={player.id}"
            >{$LL.PLAYERS.PROFILE.EDIT_PROFILE()}</Button
          >
          <Button on:click={() => (show_notes = !show_notes)}>
            {#if show_notes}
              {$LL.PLAYERS.PROFILE.HIDE_PLAYER_NOTES()}
            {:else}
              {$LL.PLAYERS.PROFILE.SHOW_PLAYER_NOTES()}
            {/if}
          </Button>
          <Button on:click={openEditPlayerNotesDialog}>{$LL.PLAYERS.PROFILE.EDIT_PLAYER_NOTES()}</Button>
          {#if player.user_settings}
            <Button on:click={sendPasswordReset}>{$LL.PLAYERS.PROFILE.SEND_PASSWORD_RESET()}</Button>
          {/if}
        {/if}
        {#if check_permission(user_info, permissions.edit_user) && player.user_settings}
          <Button href="/{$page.params.lang}/moderator/users/edit?id={player.user_settings.user_id}"
            >{$LL.MODERATOR.MANAGE_USERS.EDIT_USER()}</Button
          >
        {/if}
        {#if check_permission(user_info, permissions.view_alt_flags)}
          <PlayerAltFlags bind:this={altDialog} player_id={player.id} />
          <Button on:click={altDialog.open}>{$LL.MODERATOR.ALT_DETECTION.ALT_FLAGS()}</Button>
        {/if}
        {#if check_permission(user_info, permissions.view_user_logins)}
          <PlayerLogins bind:this={loginDialog} player_id={player.id} />
          <Button on:click={loginDialog.open}>{$LL.MODERATOR.ALT_DETECTION.LOGIN_HISTORY()}</Button>
        {/if}
        {#if check_permission(user_info, permissions.view_basic_ip_info)}
          <PlayerIpDialog bind:this={ipDialog} player_id={player.id} />
          <Button on:click={ipDialog.open}>{$LL.MODERATOR.ALT_DETECTION.IP_HISTORY()}</Button>
        {/if}
      </div>
      {#if show_notes}
        <PlayerNotes notes={player.notes} />
      {/if}
    </Section>
  {/if}
  <PlayerProfile {player} />
  <PlayerTournamentHistory {player} />
  <PlayerRegistrationHistory {player} />
  {#if user_info.player && player.is_shadow}
    <ClaimPlayer {player} />
  {/if}
{:else if !player_found}
  {$LL.PLAYERS.PROFILE.PLAYER_NOT_FOUND()}
{/if}
