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
  let setting = "any";

  onMount(async () => {
    const res = await fetch(`/api/tournaments/${tournament.id}/registrations`);
    if(res.status < 300) {
      const body = await res.json();
      if (tournament.is_squad) {
        tournament_squads = body;
        registration_count = tournament_squads.length;
      } else {
        tournament_players = body;
        registration_count = tournament_players.length;
      }
      registrations_loaded = true;
    }
  });

  async function filter_registrations() {
    let eligible_only = false;
    let hosts_only = false;
    if(setting === "eligible" || setting === "hosts") {
      eligible_only = true;
    }
    if(setting === "hosts") {
      hosts_only = true
    }
    const res = await fetch(`/api/tournaments/${tournament.id}/registrations?eligible_only=${eligible_only}&hosts_only=${hosts_only}`);
    if(res.status < 300) {
      const body = await res.json();
      console.log(body);
      if (tournament.is_squad) {
        tournament_squads = body;
        registration_count = tournament_squads.length;
      } else {
        tournament_players = body;
        registration_count = tournament_players.length;
      }
    }
  }
</script>

<div>
  {#if registrations_loaded}
    <div>
      <select bind:value={setting} on:change={filter_registrations}>
        <option value={"any"}>All {tournament.is_squad ? "Squads" : "Players"}</option>
        {#if tournament.is_squad}
          <option value={"eligible"}>Eligible Only</option>
        {/if}
        {#if tournament.host_status_required}
          <option value={"hosts"}>Hosts Only</option>
        {/if}
        
      </select>
    </div>
    {#if registration_count > 0}
      <div>
        {registration_count} {tournament.is_squad ? "Squads" : "Players"}
      </div>
      {#if tournament.is_squad}
        <TournamentSquadList {tournament} squads={tournament_squads} />
      {:else}
        <TournamentPlayerList {tournament} players={tournament_players} />
      {/if}
    {:else}
      No {tournament.is_squad ? 'squad' : 'player'}s. Be the first to register!
    {/if}
  {/if}
</div>
