<script lang="ts">
    import { onMount } from 'svelte';
    import type { PlayerInfo } from '$lib/types/player-info';
    import Section from '$lib/components/common/Section.svelte';
    import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
    import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
  
    let player: PlayerInfo | null = null;
  
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
  
<Section header='Ban Player'>
  <PlayerSearch bind:player={player}/>
  {#if player}
    <br/>
    <BanPlayerForm player={player}/>
  {/if}
</Section>
  