<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import LL from '$i18n/i18n-svelte';
  import PlayerProfileEdit from '$lib/components/registry/players/PlayerProfileEdit.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  $: player = user_info.player ? user_info.player : null;
</script>

<svelte:head>
  <title>{$LL.PLAYERS.PROFILE.EDIT_PROFILE()} | Mario Kart Central</title>
</svelte:head>

{#if player}
  <PlayerProfileEdit {player}/>
{/if}
