<script lang="ts">
    import LL from '$i18n/i18n-svelte';
    import PlayerProfileEdit from '$lib/components/registry/players/PlayerProfileEdit.svelte';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { PlayerInfo } from '$lib/types/player-info';

    let player: PlayerInfo;

    onMount(async() => {
        let param_id = $page.url.searchParams.get('id');
        let id = Number(param_id);
        const res = await fetch(`/api/registry/players/${id}`);
        if (res.status != 200) {
            return;
        }
        const body: PlayerInfo = await res.json();
        player = body;
    })
  </script>
  
  <svelte:head>
    <title>{$LL.PLAYER_PROFILE.EDIT_PROFILE()} | Mario Kart Central</title>
  </svelte:head>
  
  {#if player}
    <PlayerProfileEdit {player}/>
  {/if}
  