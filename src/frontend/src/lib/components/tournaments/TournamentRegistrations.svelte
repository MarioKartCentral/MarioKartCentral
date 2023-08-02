<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import { onMount } from 'svelte';
  import TournamentSquadList from './TournamentSquadList.svelte';
  import TournamentPlayerList from './TournamentPlayerList.svelte';

  export let tournament: Tournament;
  let tournament_squads: TournamentSquad[];
  let tournament_players: TournamentPlayer[];
  let registrations_loaded = false;
  let registration_count = 0;

  onMount(async () => {
    const res = await fetch(`/api/tournaments/${tournament.id}/registrations?`);
    const body = await res.json();
    if (tournament.is_squad) {
      tournament_squads = body;
      registration_count = tournament_squads.length;
    } else {
      tournament_players = body;
      registration_count = tournament_players.length;
    }
    registrations_loaded = true;
  });
</script>

<div>
  {#if registrations_loaded}
    {#if registration_count > 0}
      {#if tournament.is_squad}
        <TournamentSquadList {tournament} squads={tournament_squads} />
      {:else}
        <TournamentPlayerList {tournament} players={tournament_players} />
      {/if}
    {:else}
      No {tournament.is_squad ? "squad" : "player"}s. Be the first to register!
    {/if}
  {/if}
</div>
