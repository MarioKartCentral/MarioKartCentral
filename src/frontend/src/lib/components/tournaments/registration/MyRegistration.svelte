<script lang="ts">
  import type { MyTournamentRegistration, RegistrationDetails } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import TournamentInviteList from './TournamentInviteList.svelte';
  import MySquad from './MySquad.svelte';
  import TournamentPlayerList from '../TournamentPlayerList.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { BadgeCheckSolid } from 'flowbite-svelte-icons';

  export let registration: MyTournamentRegistration;
  export let tournament: Tournament;

  function getInvitedSquads() {
    let invite_registrations = registration.registrations.filter((r) => r.player.is_invite);
    // this line is mostly for the linter to know that none of the squad values will be null
    return invite_registrations.map((r) => r.squad).filter((s) => s !== null);
  }

  async function toggleCheckin(reg: RegistrationDetails) {
    const payload = {
      tournament_id: tournament.id,
      squad_id: reg.player.squad_id,
      player_id: reg.player.player_id
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

{#if tournament.is_squad}
  {#if getInvitedSquads().length}
    <div>My invites</div>
    <TournamentInviteList {tournament} squads={getInvitedSquads()}/>
  {/if}
{/if}
  {#each registration.registrations.filter((r) => !r.player.is_invite) as reg}
    <div class="registration">
      {#if tournament.checkins_enabled}
        <div class="section">
          {#if tournament.checkins_open}
            {#if !reg.player.is_checked_in}
              <Button on:click={() => toggleCheckin(reg)}>Check In Now!</Button>
              <div>
                Make sure to check in before the tournament starts!
              </div>
            {:else}
              <div class="flex">
                <BadgeCheckSolid/>
                <div>
                  CHECKED IN
                </div>
                {#if reg.squad}
                  <div>
                    ({reg.squad.players.filter((p) => p.is_checked_in).length}/{tournament.min_players_checkin})
                  </div>
                {/if}
              </div>
              <div>
                <Button size="xs" on:click={() => toggleCheckin(reg)}>Check Out</Button>
              </div>
            {/if}
          {:else}
            Make sure to check in during the check-in window!
          {/if}
        </div>
      {/if}
      {#if tournament.verification_required && ((reg.squad && !reg.squad.is_approved) || (!reg.squad && !reg.player.is_approved))}
        <div class="section">
          <div class="pending">
            Pending Approval
          </div>
          Your registration must be approved before you can play.
        </div>
      {/if}
      {#if reg.squad}
        <MySquad {tournament} squad={reg.squad} my_player={reg.player}/>
      {:else}
        <div>My Registration</div>
        <TournamentPlayerList {tournament} players={[reg.player]} my_player={reg.player}/>
      {/if}
    </div>
  {/each}

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
  div.registration {
    padding-bottom: 10px;
    border-bottom: 1px white solid;
  }
</style>