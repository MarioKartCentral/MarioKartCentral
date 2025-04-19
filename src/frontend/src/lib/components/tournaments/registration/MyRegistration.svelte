<script lang="ts">
  import type { MyTournamentRegistration, RegistrationDetails } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import TournamentInviteList from './TournamentInviteList.svelte';
  import MySquad from './MySquad.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { BadgeCheckSolid } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';

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
      registration_id: reg.player.registration_id,
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
      alert(`${$LL.TOURNAMENTS.REGISTRATIONS.CHECK_IN_OUT_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if tournament.is_squad}
  {#if getInvitedSquads().length}
    <div>
      {$LL.TOURNAMENTS.REGISTRATIONS.MY_INVITES()}
    </div>
    <TournamentInviteList {tournament} squads={getInvitedSquads()}/>
  {/if}
{/if}
{#each registration.registrations.filter((r) => !r.player.is_invite) as reg}
  <div class="registration">
    {#if tournament.checkins_enabled}
      <div class="section">
        {#if tournament.checkins_open}
          {#if !reg.player.is_checked_in}
            <Button on:click={() => toggleCheckin(reg)}>{$LL.TOURNAMENTS.REGISTRATIONS.CHECK_IN_BUTTON()}</Button>
            <div>
              {$LL.TOURNAMENTS.REGISTRATIONS.CHECK_IN_REMINDER_WINDOW_OPEN()}
            </div>
          {:else}
            <div class="flex">
              <BadgeCheckSolid/>
              <div>
                {$LL.TOURNAMENTS.REGISTRATIONS.CHECKED_IN()}
              </div>
              {#if reg.squad}
                <div>
                  ({reg.squad.players.filter((p) => p.is_checked_in).length}/{tournament.min_players_checkin})
                </div>
              {/if}
            </div>
            <div>
              <Button size="xs" on:click={() => toggleCheckin(reg)}>{$LL.TOURNAMENTS.REGISTRATIONS.CHECK_OUT()}</Button>
            </div>
          {/if}
        {:else}
          {$LL.TOURNAMENTS.REGISTRATIONS.CHECK_IN_REMINDER_WINDOW_CLOSED()}
        {/if}
      </div>
    {/if}
    {#if tournament.verification_required && ((reg.squad && !reg.squad.is_approved) || (!reg.squad && !reg.player.is_approved))}
      <div class="section">
        <div class="pending">
          {$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATION_PENDING_APPROVAL()}
        </div>
        {$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATION_PENDING_MESSAGE()}
      </div>
    {/if}
    <MySquad {tournament} squad={reg.squad} my_player={reg.player}/>
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
    margin-bottom: 10px;
    border-bottom: 1px white solid;
  }
</style>