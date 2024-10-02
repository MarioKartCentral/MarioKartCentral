<script lang="ts">
  import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import TournamentInviteList from './TournamentInviteList.svelte';
  import MySquad from './MySquad.svelte';
  import TournamentPlayerList from '../TournamentPlayerList.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { BadgeCheckSolid } from 'flowbite-svelte-icons';

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

  async function toggleCheckin() {
    if(!registration.player) return;
    const payload = {
      tournament_id: tournament.id,
      squad_id: registration.player.squad_id,
      player_id: registration.player.player_id
    }
    const endpoint = `/api/tournaments/${tournament.id}/toggleCheckin`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`Failed to check in/out: ${result['title']}`);
    }
  }
</script>

{#if tournament.checkins_enabled && registration.player}
  <div class="section">
    {#if tournament.checkins_open}
        {#if !registration.player.is_checked_in}
          <Button on:click={toggleCheckin}>Check In Now!</Button>
          <div>
            Make sure to check in before the tournament starts!
          </div>
        {:else}
          <div class="flex">
            <BadgeCheckSolid/>
            <div>
              CHECKED IN
            </div>
            {#if squad}
              <div>
                ({squad.players.filter((p) => p.is_checked_in).length}/{tournament.min_players_checkin})
              </div>
            {/if}
          </div>
          <div>
            <Button size="xs" on:click={toggleCheckin}>Check Out</Button>
          </div>
        {/if}
    {:else}
      Make sure to check in during the check-in window!
    {/if}
  </div>
{/if}
{#if tournament.is_squad}
  {#if getInvites().length}
    <div>My invites</div>
    <TournamentInviteList {tournament} squads={getInvites()}/>
  {/if}
  {#if squad && registration.player}
    {#if tournament.verification_required && !squad.is_approved}
      <div class="section">
        <div class="pending">
          Pending Approval
        </div>
        Your registration must be approved before you can play.
      </div>
    {/if}
    <MySquad {tournament} {squad} my_player={registration.player}/>
  {/if}
{:else}
  {#if registration.player}
    {#if tournament.verification_required && !registration.player.is_approved}
      <div class="section">
        <div class="pending">
          Pending Approval
        </div>
        Your registration must be approved before you can play.
      </div>
    {/if}
    <div>My Registration</div>
    <TournamentPlayerList {tournament} players={[registration.player]} my_player={registration.player}/>
  {/if}
{/if}

<style>
  div.pending {
    font-size: large;
  }
  div.section {
    margin: 10px 0;
  }
  div.flex {
    display: flex;
    gap: 5px;
  }
</style>