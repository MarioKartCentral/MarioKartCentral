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
  import LL from '$i18n/i18n-svelte';

  export let tournament: Tournament;
  let tournament_squads: TournamentSquad[];
  let tournament_players: TournamentPlayer[];
  let registrations_loaded = false;
  let registration_count = 0;
  let setting = 'any';

  let user_info: UserInfo;

  let show_all = false;
  let display_limit = 12;

  user.subscribe((value) => {
    user_info = value;
  });

  async function fetchData() {
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
      tournament_squads = body;
      registration_count = tournament_squads.length;
      console.log(tournament_squads);
      if(!tournament.is_squad) {
        tournament_players = tournament_squads.flatMap((squad) => squad.players);
        
      }
      show_all = false;
      registrations_loaded = true;
    }
  }

  onMount(async () => {
    await fetchData();
  });

</script>

<div>
  {#if registrations_loaded}
    <div>
      <select bind:value={setting} on:change={fetchData}>
        <option value={'any'}>
          {$LL.TOURNAMENTS.REGISTRATIONS.ALL_REGISTRATIONS({is_squad: tournament.is_squad})}
        </option>
        {#if tournament.is_squad || tournament.checkins_enabled}
          <option value={'eligible'}>{$LL.TOURNAMENTS.REGISTRATIONS.ELIGIBLE_ONLY()}</option>
        {/if}
        {#if tournament.host_status_required}
          <option value={'hosts'}>{$LL.TOURNAMENTS.REGISTRATIONS.HOSTS_ONLY()}</option>
        {/if}
        {#if tournament.verification_required && check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
          tournament.id, tournament.series_id)}
          <option value={'pending'}>{$LL.TOURNAMENTS.REGISTRATIONS.PENDING()}</option>
        {/if}
      </select>
    </div>
    {#if registration_count > 0}
      <div>
        {#if tournament.is_squad}
          {$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_COUNT({count: registration_count})}
        {:else}
          {$LL.TOURNAMENTS.REGISTRATIONS.PLAYER_COUNT({count: registration_count})}
        {/if}
        {#if !show_all && registration_count > display_limit}
          <button class="show-players" on:click={() => show_all = true}>{$LL.TOURNAMENTS.REGISTRATIONS.SHOW_ALL_PLAYERS()}</button>
        {/if}
      </div>
      {#if tournament.is_squad}
        {#key [tournament_squads, show_all]}
          <TournamentSquadList {tournament} squads={show_all ? tournament_squads : tournament_squads.slice(0, display_limit)} is_privileged={check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
            tournament.id, tournament.series_id
          )}/>
        {/key}
      {:else}
        {#key [tournament_players, show_all]}
          <TournamentPlayerList {tournament} players={show_all ? tournament_players : tournament_players.slice(0, display_limit)} is_privileged={check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations,
            tournament.id, tournament.series_id
          )}/>
        {/key}
      {/if}
    {:else}
      {$LL.TOURNAMENTS.REGISTRATIONS.NO_REGISTRATIONS({is_squad: tournament.is_squad})}
    {/if}
  {/if}
</div>

<style>
  button.show-players {
    background-color: transparent;
    border: none;
    color: white;
    cursor: pointer;
  }
</style>