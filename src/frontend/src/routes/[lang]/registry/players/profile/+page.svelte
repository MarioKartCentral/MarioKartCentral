<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import Button from "$lib/components/common/buttons/Button.svelte";
  import Dialog from '$lib/components/common/Dialog.svelte';
  import PlayerProfile from '$lib/components/registry/players/PlayerProfile.svelte';
  import PlayerProfileBan from '$lib/components/registry/players/PlayerProfileBan.svelte';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';
  import { permissions } from '$lib/util/util';

  let banDialog: Dialog;
  let editBanDialog: Dialog;

  let id = 0;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  let player_found = true;
  let player: PlayerInfo;
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
  });
</script>

<svelte:head>
  <title>{player_name} | Mario Kart Central</title>
</svelte:head>

{#if player}
  {#if player.ban_info}
    <PlayerProfileBan ban_info={player.ban_info} />
  {/if}
  <PermissionCheck permission={permissions.ban_player}>
    <Section header={$LL.NAVBAR.MODERATOR()}>
      <div slot="header_content">
        {#if !player.is_banned}
          <Button on:click={banDialog.open}>{$LL.PLAYER_BAN.BAN_PLAYER()}</Button>
        {:else}
          <Button on:click={editBanDialog.open}>{$LL.PLAYER_BAN.VIEW_EDIT_BAN()}</Button>
        {/if}
      </div>
    </Section>
    <Dialog bind:this={banDialog} header={$LL.PLAYER_BAN.BAN_PLAYER()}>
      <BanPlayerForm player={player} handleCancel={() => banDialog.close()}/>
    </Dialog>
    <Dialog bind:this={editBanDialog} header={$LL.PLAYER_BAN.VIEW_EDIT_BAN()}>
      <ViewEditBan player={player}/>
    </Dialog>
  </PermissionCheck>
  <PlayerProfile {player} />
{/if}
