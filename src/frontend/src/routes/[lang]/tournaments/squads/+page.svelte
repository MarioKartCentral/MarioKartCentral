<script lang="ts">
  import { page } from '$app/stores';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import { onMount } from 'svelte';
  let squad: TournamentSquad;
  let id;
  let tournament_id;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    let param_tournament_id = $page.url.searchParams.get('tournament_id');
    id = Number(param_id);
    tournament_id = Number(param_tournament_id);
    const res = await fetch(`/api/tournaments/${tournament_id}/squads/${id}`);
    if (res.status !== 200) {
      return;
    }
    const body = await res.json();
    squad = body;
  });
</script>

<div>{squad?.tag} - {squad?.name}</div>
{#if squad?.players}
  {#each squad.players as player}
    <div>{player?.name}</div>
  {/each}
{/if}
