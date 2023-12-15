<script lang="ts">
    import type { MyTournamentRegistration } from "$lib/types/tournaments/my-tournament-registration";
    import type { Tournament } from "$lib/types/tournament";
    import Table from "$lib/components/common/Table.svelte";
    import TournamentPlayerList from "../TournamentPlayerList.svelte";

    export let registration: MyTournamentRegistration;
    export let tournament: Tournament;

    let registration_deadline: Date | null = tournament.registration_deadline ? new Date(tournament.registration_deadline * 1000) : null;

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
            return false;
        }
        let now = new Date().getTime();
        if (registration_deadline.getTime() < now) {
            return false;
        }
        return true;
    }

    async function invitePlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if(!registration.player) {
            return;
        }
        if(!registration.player.is_squad_captain) {
            return;
        }
        const formData = new FormData(event.currentTarget);
        let player_id = Number(formData.get("player_id"));
        const payload = {
            squad_id: registration.player.squad_id,
            player_id: player_id,
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
              </tr>
            </thead>
            <tbody>
              {#each squad.players.filter((p) => !p.is_invite) as player, i}
                <tr class="row-{i % 2}">
                  <td>{player.country_code}</td>
                  <td>{player.name}</td>
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
                </tr>
              {/each}
            </tbody>
          </Table>

          {#if squad.players.filter((p) => p.is_invite).length > 0}
            <div>{squad.players.filter((p) => p.is_invite).length} invited players</div>
            <Table>
                <col class="country" />
                <col class="name" />
                {#if tournament.mii_name_required}
                <col class="mii-name" />
                {/if}
                {#if tournament.host_status_required}
                <col class="can-host" />
                {/if}
                <col class="friend-codes" />
                
                <thead>
                <tr>
                    <th />
                    <th>Name</th>
                    {#if tournament.mii_name_required}
                    <th/>
                    {/if}
                    
                    {#if tournament.host_status_required}
                    <th/>
                    {/if}
                    <th>Cancel invitation</th>
                </tr>
                </thead>
                <tbody>
                {#each squad.players.filter((p) => p.is_invite) as player, i}
                    <tr class="row-{i % 2}">
                    <td>{player.country_code}</td>
                    <td>{player.name}</td>
                    {#if tournament.mii_name_required}
                        <td/>
                    {/if}
                    {#if tournament.host_status_required}
                        <td/>
                    {/if}
                    <td>
                        <button on:click={() => cancelInvite(player.player_id)}>Cancel</button>
                    </td>
                    
                    </tr>
                {/each}
                </tbody>
            </Table>
          {/if}

        <!-- If registrations are open and our squad is not full and we are the squad captain -->
        {#if check_registrations_open() && (!tournament.max_squad_size || squad.players.length <= tournament.max_squad_size) && registration.player?.is_squad_captain}
            <div>Invite players</div>
            <form method="POST" on:submit|preventDefault={invitePlayer}>
                <input name="player_id" type="number" min=1 required/>
                <button type="submit">Submit</button>
            </form>
        {/if}
    {/each}

    {#if !registration.player}
        <div>My invites</div>
        {#each getInvites() as invite}
            <div>{invite.tag}</div>
        {/each}
    {/if}
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
      width: 30%;
    }
    col.mii-name {
      width: 30%;
    }
    col.friend-codes {
      width: 25%;
    }
    col.can-host {
      width: 10%;
    }
  </style>
  