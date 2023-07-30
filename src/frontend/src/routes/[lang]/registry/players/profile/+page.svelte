<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import PlayerProfile from '$lib/components/PlayerProfile.svelte';
  import PlayerProfileBan from '$lib/components/PlayerProfileBan.svelte';

  let id = 0;
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
  <div class="container">
    {#if player.ban_info}
      <PlayerProfileBan ban_info={player.ban_info} />
    {/if}
    <PlayerProfile {player} />
  </div>
{/if}

<style>
  .container {
    width: 50%;
    margin: 20px auto 20px auto;
  }
</style>
