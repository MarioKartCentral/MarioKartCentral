<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  import ViewEditBan from '$lib/components/moderator/ViewEditBan.svelte';

  let player: PlayerInfo | null = null;
  let playerDetailed: PlayerInfo | null = null;

  $: updatePlayerDetailed(player)

  async function updatePlayerDetailed(player: PlayerInfo) {
    if (!player) {
      playerDetailed = null
      return
    }

    const res = await fetch(`/api/registry/players/${player.id}`);
    if (res.status === 200) {
      playerDetailed = await res.json()
    }
  }

  function handleCancel() {
    player = null
  }

  onMount(async () => {
    // let param_id = $page.url.searchParams.get('id');
    // id = Number(param_id);
    // const res = await fetch(`/api/registry/players/${id}`);
    // if (res.status != 200) {
    //   player_found = false;
    //   return;
    // }
    // const body: PlayerInfo = await res.json();
    // player = body;
  });
</script>

<svelte:head>
  <title>Player Bans | Mario Kart Central</title>
</svelte:head>

<Section header={$LL.PLAYER_BAN.BAN_PLAYER()}>
  <PlayerSearch bind:player={player}/>
  {#if playerDetailed}
    {#if playerDetailed.ban_info}
      <strong>{$LL.PLAYER_BAN.THE_PLAYER_IS_ALREADY_BANNED()}</strong>
      <hr/>
      <ViewEditBan player={playerDetailed}/>
    {:else}
      <br/>
      <BanPlayerForm player={playerDetailed} {handleCancel}/>
    {/if}
  {/if}
</Section>

<Section header={$LL.PLAYER_BAN.LIST_OF_BANNED_PLAYERS()}>
  Coming soon...
</Section>

<Section header={$LL.PLAYER_BAN.LIST_OF_HISTORICAL_BANS()}>
  Coming soon...
</Section>

<style>
hr {
  margin: 10px 0px;
}
</style>