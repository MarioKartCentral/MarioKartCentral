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
    import Dialog from "$lib/components/common/Dialog.svelte";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";

    export let registration: MyTournamentRegistration;
    export let tournament: Tournament;
    export let friend_codes: FriendCode[];

    let invite_player: PlayerInfo | null = null;
    let edit_reg_dialog: Dialog;

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

    async function editRegistration(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get("selected_fc_id");
        let mii_name = formData.get("mii_name");
        let can_host = formData.get("can_host");
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === "true",
            squad_id: registration.player?.squad_id
        };
        const endpoint = `/api/tournaments/${tournament.id}/editMyRegistration`;
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
            alert(`Editing registration failed: ${result['title']}`);
        }
    }
</script>

{#if tournament.is_squad}
    {#if getInvites().length}
      <div>My invites</div>
      <TournamentInviteList {tournament} squads={getInvites()} {friend_codes}/>
    {/if}
    {#if squad}
      <MySquad {tournament} {squad} {registration} {friend_codes}/>
    {/if}
{:else}
    <div>My Registration</div>
    {#if registration.player}
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
            <tr>
            <td>{registration.player.country_code}</td>
            <td>{registration.player.name}</td>
            {#if tournament.mii_name_required}
                <td>{registration.player.mii_name}</td>
            {/if}
            <td>
                {#if registration.player.friend_codes.length > 0}
                {registration.player.friend_codes[0]}
                {/if}
            </td>
            {#if tournament.host_status_required}
                <td>{registration.player.can_host ? 'Yes' : 'No'}</td>
            {/if}
            <td>
              <button on:click={edit_reg_dialog.open}>Edit</button>
              <button on:click={unregister}>Unregister</button>
            </td>
            </tr>
        </tbody>
      </Table>
    {/if}
{/if}
  
<Dialog bind:this={edit_reg_dialog} header="Edit Player Registration">
  <form method="POST" on:submit|preventDefault={editRegistration}>
      <SoloTournamentFields {tournament} {friend_codes} mii_name={registration.player?.mii_name} can_host={registration.player?.can_host}/>
      <br/>
      <div>
          <button type="submit">Edit Registration</button>
          <button type="button" on:click={edit_reg_dialog.close}>Cancel</button>
      </div>
  </form>
</Dialog>

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
  col.actions {
    width: 10%;
  }
</style>