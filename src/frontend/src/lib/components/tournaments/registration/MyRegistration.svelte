<script lang="ts">
  import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import TournamentInviteList from './TournamentInviteList.svelte';
  import MySquad from './MySquad.svelte';
  import TournamentPlayerList from '../TournamentPlayerList.svelte';

  export let registration: MyTournamentRegistration;
  export let tournament: Tournament;

  function getRegSquad() {
    for (let squad of registration.squads) {
      if (squad.id === registration.player?.squad_id) {
        return squad;
      }
    }
    return null;
  }

  let squad = getRegSquad();

  function getInvites() {
    let squads = [];
    for (let squad of registration.squads) {
      if (squad.id !== registration.player?.squad_id) {
        squads.push(squad);
      }
    }
    return squads;
  }
</script>

{#if tournament.is_squad}
  {#if getInvites().length}
    <div>My invites</div>
    <TournamentInviteList {tournament} squads={getInvites()}/>
  {/if}
  {#if squad && registration.player}
    <MySquad {tournament} {squad} my_player={registration.player}/>
  {/if}
{:else}
  <div>My Registration</div>
  {#if registration.player}
    <TournamentPlayerList {tournament} players={[registration.player]} my_player={registration.player}/>
  {/if}
{/if}
