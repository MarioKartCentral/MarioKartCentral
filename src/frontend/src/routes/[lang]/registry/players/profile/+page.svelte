<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { BanListData, BanInfoDetailed } from '$lib/types/ban-info';
  import Section from '$lib/components/common/Section.svelte';
  import Button from "$lib/components/common/buttons/Button.svelte";
  import Dialog from '$lib/components/common/Dialog.svelte';
  import PlayerProfile from '$lib/components/registry/players/PlayerProfile.svelte';
  import PlayerProfileBan from '$lib/components/registry/players/PlayerProfileBan.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import ClaimPlayer from '$lib/components/registry/players/ClaimPlayer.svelte';

  let user_info: UserInfo;
  let banDialog: Dialog;
  let editBanDialog: Dialog;

  user.subscribe((value) => {
    user_info = value;
  });

  let id = 0;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  let player_found = true;
  let player: PlayerInfo;
  let banInfo: BanInfoDetailed | null = null;

  $: player_name = player ? player.name : 'Registry';

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
        if (data.ban_count === 1)
          banInfo = data.ban_list[0];
      }
    }
  });
</script>

<svelte:head>
  <title>{player_name} | Mario Kart Central</title>
</svelte:head>

{#if player}
  {#if player.ban_info}
    <PlayerProfileBan ban_info={player.ban_info} />
  {/if}

  {#if check_permission(user_info, permissions.ban_player) || check_permission(user_info, permissions.edit_player)}
    <Section header={$LL.NAVBAR.MODERATOR()}>
      <div slot="header_content">
        {#if check_permission(user_info, permissions.ban_player)}
          {#if !player.is_banned}
            <Button on:click={banDialog.open}>{$LL.PLAYER_BAN.BAN_PLAYER()}</Button>
          {:else}
            <Button on:click={editBanDialog.open}>{$LL.PLAYER_BAN.VIEW_EDIT_BAN()}</Button>
          {/if}
        {/if}
        {#if check_permission(user_info, permissions.edit_player)}
          <Button href="/{$page.params.lang}/registry/players/mod-edit-profile?id={player.id}">Edit Player</Button>
        {/if}
      </div>
    </Section>
    <Dialog bind:this={banDialog} header={$LL.PLAYER_BAN.BAN_PLAYER()}>
      <BanPlayerForm playerId={player.id} playerName={player.name} handleCancel={() => banDialog.close()}/>
    </Dialog>
    <Dialog bind:this={editBanDialog} header={$LL.PLAYER_BAN.VIEW_EDIT_BAN()}>
      {#if banInfo}
        <ViewEditBan {banInfo}/>
      {/if}
    </Dialog>
    {/if}
  <PlayerProfile {player} />
  {#if user_info.player && player.is_shadow}
    <ClaimPlayer {player}/>
  {/if}
{:else if !player_found}
    Player not found
{/if}
