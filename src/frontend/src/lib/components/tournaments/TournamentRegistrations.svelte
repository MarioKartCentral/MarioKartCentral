<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import type { TournamentSquad } from '$lib/types/tournament-squad';
  import { onMount } from 'svelte';
  import TournamentSquadList from './TournamentSquadList.svelte';
  import TournamentPlayerList from './TournamentPlayerList.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';

  export let tournament: Tournament;
  let tournament_squads: TournamentSquad[];
  let tournament_players: TournamentPlayer[];
  let registrations_loaded = false;
  let registration_count = 0;
  let setting = 'any';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    const res = await fetch(`/api/tournaments/${tournament.id}/registrations?is_approved=true`);
    if (res.status < 300) {
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
    let is_approved = true;
    if (setting === 'eligible' || setting === 'hosts') {
      eligible_only = true;
    }
    if (setting === 'hosts') {
      hosts_only = true;
    }
    if (setting === 'pending') {
      is_approved = false;
    }
    
    let url = `/api/tournaments/${tournament.id}/registrations?eligible_only=${eligible_only}&hosts_only=${hosts_only}&is_approved=${is_approved}`
    const res = await fetch(url);
    if (res.status < 300) {
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
        <option value={'any'}>All {tournament.is_squad ? 'Squads' : 'Players'}</option>
        {#if tournament.is_squad}
          <option value={'eligible'}>Eligible Only</option>
        {/if}
        {#if tournament.host_status_required}
          <option value={'hosts'}>Hosts Only</option>
        {/if}
        {#if tournament.verification_required && check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
          tournament.id, tournament.series_id)}
          <option value={'pending'}>Pending</option>
        {/if}
      </select>
    </div>
    {#if registration_count > 0}
      <div>
        {registration_count}
        {tournament.is_squad ? 'Squads' : 'Players'}
      </div>
      {#if tournament.is_squad}
        {#key tournament_squads}
          <TournamentSquadList {tournament} squads={tournament_squads} is_privileged={check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
            tournament.id, tournament.series_id
          )}/>
        {/key}
      {:else}
        {#key tournament_players}
          <TournamentPlayerList {tournament} players={tournament_players} is_privileged={check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
            tournament.id, tournament.series_id
          )}/>
        {/key}
      {/if}
    {:else}
      No {tournament.is_squad ? 'squad' : 'player'}s. Be the first to register!
    {/if}
  {/if}
</div>
