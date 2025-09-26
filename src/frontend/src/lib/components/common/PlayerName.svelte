<script lang="ts">
  import type { PlayerBasic } from '$lib/types/player';
  import { page } from '$app/stores';
  import Flag from './Flag.svelte';

  export let player: PlayerBasic;
</script>

<a href="/{$page.params.lang}/registry/players/profile?id={player.id}">
  <div class="player">
    <Flag country_code={player.country_code} />
    {player.name}
  </div>
</a>

<style>
  .player {
    display: flex;
    gap: 5px;
    align-items: center;
  }
</style>
