<script lang="ts">
    import type { MyTournamentRegistration } from "$lib/types/tournaments/my-tournament-registration";
    import type { Tournament } from "$lib/types/tournament";
    import Table from "$lib/components/common/Table.svelte";
    import TournamentPlayerList from "../TournamentPlayerList.svelte";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import TournamentInviteList from "./TournamentInviteList.svelte";
    import type { FriendCode } from "$lib/types/friend-code";
    import MySquad from "./MySquad.svelte";

    export let registration: MyTournamentRegistration;
    export let tournament: Tournament;
    export let friend_codes: FriendCode[];

    let invite_player: PlayerInfo | null = null;

    function getRegSquad() {
        for(let squad of registration.squads) {
            if (squad.id === registration.player?.squad_id) {
                return squad;
            }
        }
        return null;
    }

    let squad = getRegSquad();

    function getInvites() {
        let squads = [];
        for(let squad of registration.squads) {
            if (squad.id !== registration.player?.squad_id) {
                squads.push(squad);
            }
        }
        return squads;
    }

    function check_registrations_open() {
        if(!tournament.registrations_open) {
            return false;
        }
        let registration_deadline: Date | null = tournament.registration_deadline ? new Date(tournament.registration_deadline * 1000) : null;
        if(!registration_deadline) {
            return true;
        }
        let now = new Date().getTime();
        if (registration_deadline.getTime() < now) {
            return false;
        }
        return true;
    }

    async function unregister() {
      if(!registration.player) {
            return;
      }
      if(registration.player.is_squad_captain && squad && squad.players.length > 1) {
        alert("Please unregister this squad or set another player as captain before unregistering for this tournament");
        return;
      }
      let conf = window.confirm("Are you sure you would like to unregister for this tournament?");
      if(!conf) {
          return;
      }
      const payload = {
        squad_id: registration.player.squad_id
      };
      console.log(payload);
      const endpoint = `/api/tournaments/${tournament.id}/unregister`;
      const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Failed to unregister: ${result['title']}`);
        }
    }
</script>

{#if tournament.is_squad}
    {#if getInvites().length}
      <div>My invites</div>
      <TournamentInviteList {tournament} squads={getInvites()} {friend_codes}/>
    {/if}
    {#if squad}
      <MySquad {tournament} {squad} {registration}/>
    {/if}
{:else}
    <div>My Registration</div>
    {#if registration.player}
        <TournamentPlayerList {tournament} players={[registration.player]}/>
    {/if}
{/if}
  