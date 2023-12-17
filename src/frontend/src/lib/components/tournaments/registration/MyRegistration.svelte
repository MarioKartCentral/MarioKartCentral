<script lang="ts">
    import type { MyTournamentRegistration } from "$lib/types/tournaments/my-tournament-registration";
    import type { Tournament } from "$lib/types/tournament";
    import Table from "$lib/components/common/Table.svelte";
    import TournamentPlayerList from "../TournamentPlayerList.svelte";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import TournamentInviteList from "./TournamentInviteList.svelte";
    import type { FriendCode } from "$lib/types/friend-code";

    export let registration: MyTournamentRegistration;
    export let tournament: Tournament;
    export let friend_codes: FriendCode[];

    let invite_player: PlayerInfo | null = null;

    function getRegSquad() {
        let squads = [];
        for(let squad of registration.squads) {
            if (squad.id === registration.player?.squad_id) {
                squads.push(squad);
            }
        }
        return squads;
    }

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

    async function invitePlayer(player: PlayerInfo | null) {
      if(!player) {
        return;
      }
      if(!registration.player) {
          return;
      }
      if(!registration.player.is_squad_captain) {
          return;
      }
      const payload = {
          squad_id: registration.player.squad_id,
          player_id: player.id,
          is_representative: false
      }
      const endpoint = `/api/tournaments/${tournament.id}/invitePlayer`;
      console.log(payload);
      const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (response.status < 300) {
          window.location.reload();
      } else {
          alert(`Invitation failed: ${result['title']}`);
      }
    }

    async function cancelInvite(player_id: number) {
        if(!registration.player) {
            return;
        }
        if(!registration.player.is_squad_captain) {
            return;
        }
        let conf = window.confirm("Are you sure you would like to cancel this invite?");
        if(!conf) {
            return;
        }
        const payload = {
            squad_id: registration.player.squad_id,
            player_id: player_id
        }
        const endpoint = `/api/tournaments/${tournament.id}/kickPlayer`;
        console.log(payload);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Cancelling invite failed: ${result['title']}`);
        }
    }
</script>

{#if tournament.is_squad}
    {#if getInvites().length}
      <div>My invites</div>
      <TournamentInviteList {tournament} squads={getInvites()} {friend_codes}/>
    {/if}
    {#each getRegSquad() as squad}
        <div>My squad</div>
        <div>{squad.players.filter((p) => !p.is_invite).length} players</div>
        <Table>
            <col class="country" />
            <col class="name" />
            {#if tournament.mii_name_required}
              <col class="mii-name" />
            {/if}
            <col class="friend-codes" />
            {#if tournament.host_status_required}
              <col class="can-host" />
            {/if}
            <col class="actions"/>
            <thead>
              <tr>
                <th />
                <th>Name</th>
                {#if tournament.mii_name_required}
                  <th>In-Game Name</th>
                {/if}
                <th>Friend Codes</th>
                {#if tournament.host_status_required}
                  <th>Can Host</th>
                {/if}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each squad.players.filter((p) => !p.is_invite) as player, i}
                <tr class="row-{i % 2}">
                  <td>{player.country_code}</td>
                  <td>{player.name} {player.is_squad_captain ? "(Captain)" : ""}</td>
                  {#if tournament.mii_name_required}
                    <td>{player.mii_name}</td>
                  {/if}
                  <td>
                    {#if player.friend_codes.length > 0}
                      {player.friend_codes[0]}
                    {/if}
                  </td>
                  {#if tournament.host_status_required}
                    <td>{player.can_host ? 'Yes' : 'No'}</td>
                  {/if}
                  <td>
                    {#if registration.player?.player_id === player.player_id}
                      <button>Unregister</button>
                    {:else if registration.player?.is_squad_captain}
                      <button>Kick</button>
                      <button>Captain</button>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </Table>

          {#if squad.players.filter((p) => p.is_invite).length > 0}
            <div>{squad.players.filter((p) => p.is_invite).length} invited players</div>
            <Table>
                <col class="country" />
                <col class="name" />
                <col class="friend-codes" />
                <col class="cancel-invite" />
                
                <thead>
                <tr>
                    <th />
                    <th>Name</th>
                    <th>Friend Codes</th>
                    
                    <th>Cancel invitation</th>
                </tr>
                </thead>
                <tbody>
                {#each squad.players.filter((p) => p.is_invite) as player, i}
                    <tr class="row-{i % 2}">
                    <td>{player.country_code}</td>
                    <td>{player.name}</td>
                    
                    <td>
                      {#if player.friend_codes.length > 0}
                        {player.friend_codes[0]}
                      {/if}
                    </td>

                    <td>
                        <button on:click={() => cancelInvite(player.player_id)}>Cancel</button>
                    </td>
                    
                    </tr>
                {/each}
                </tbody>
            </Table>
          {/if}

        <!-- If registrations are open and our squad is not full and we are the squad captain -->
        {#if check_registrations_open() && (!tournament.max_squad_size || squad.players.length < tournament.max_squad_size) && registration.player?.is_squad_captain}
            <div>Invite players</div>
            <PlayerSearch bind:player={invite_player} game={tournament.game}/>
            {#if invite_player}
              <button on:click={() => invitePlayer(invite_player)}>Invite</button>
            {/if}
        {/if}
    {/each}

{:else}
    <div>My Registration</div>
    {#if registration.player}
        <TournamentPlayerList {tournament} players={[registration.player]}/>
    {/if}
{/if}

<style>
    col.country {
      width: 5%;
    }
    col.name {
      width: 25%;
    }
    col.mii-name {
      width: 25%;
    }
    col.friend-codes {
      width: 25%;
    }
    col.can-host {
      width: 10%;
    }
    col.cancel-invite {
      width: 25%;
    }
    col.actions {
      width: 10%;
    }
  </style>
  