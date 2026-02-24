<script lang="ts">
  import Flag from '$lib/components/common/Flag.svelte';
  import type { PlacementOrganizer } from '$lib/types/placement-organizer';
  import { page } from '$app/stores';

  export let placement: PlacementOrganizer;
  const { squad } = placement;
</script>

{#if squad.name || squad.players.length > 4}
  <span>{squad.name || `Squad ${squad.id}`}</span>
  {#if placement.description}
    <div class="text-white">{placement.description}</div>
  {/if}
{:else}
  <div class="grid">
    {#each squad.players as player (player.id)}
      <a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}" class="truncate">
        <Flag country_code={player.country_code} size="small" />
        <span class="ml-1">{player.name}</span>
      </a>
    {/each}
    {#if placement.description}
      <div class="self-center text-white">{placement.description}</div>
    {/if}
  </div>
{/if}

<style>
  .grid {
    grid-template-columns: repeat(2, minmax(auto, 180px));
  }
</style>
