<script lang="ts">
  import type { PlayerBasic } from '$lib/types/player';
  import { page } from '$app/stores';
  import Flag from './Flag.svelte';

  export let player: PlayerBasic;
</script>

<a href="/{$page.params.lang}/registry/players/profile?id={player.id}">
  <div class="player">
    <Flag country_code={player.country_code} />
    <span class={player.is_banned ? 'banned_name' : ''}>
      {player.name}
    </span>
  </div>
</a>

<style>
  .player {
    display: flex;
    gap: 5px;
    align-items: center;
  }
  .banned_name {
    opacity: 0.7;
    text-decoration: line-through;
  }
</style>
