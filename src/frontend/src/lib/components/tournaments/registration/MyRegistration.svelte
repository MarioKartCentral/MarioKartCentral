<script lang="ts">
  import type { MyTournamentRegistration } from '$lib/types/tournaments/my-tournament-registration';
  import type { Tournament } from '$lib/types/tournament';
  import Table from '$lib/components/common/Table.svelte';
  import TournamentInviteList from './TournamentInviteList.svelte';
  import type { FriendCode } from '$lib/types/friend-code';
  import MySquad from './MySquad.svelte';
    import Flag from '$lib/components/common/Flag.svelte';
    import Dropdown from '$lib/components/common/Dropdown.svelte';
    import DropdownItem from '$lib/components/common/DropdownItem.svelte';
    import { ChevronDownSolid } from 'flowbite-svelte-icons';
    import PlayerName from './PlayerName.svelte';
    import { check_registrations_open, unregister } from '$lib/util/util';
    import EditMyRegistration from './EditMyRegistration.svelte';

  export let registration: MyTournamentRegistration;
  export let tournament: Tournament;
  export let friend_codes: FriendCode[];

  let edit_reg_dialog: EditMyRegistration;

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
    <TournamentInviteList {tournament} squads={getInvites()} {friend_codes} />
  {/if}
  {#if squad}
    <MySquad {tournament} {squad} {registration} {friend_codes} />
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
      <col class="friend-codes mobile-hide" />
      {#if tournament.host_status_required}
        <col class="can-host mobile-hide" />
      {/if}
      <col class="actions" />
      <thead>
        <tr>
          <th />
          <th>Name</th>
          {#if tournament.mii_name_required}
            <th>In-Game Name</th>
          {/if}
          <th class="mobile-hide">Friend Codes</th>
          {#if tournament.host_status_required}
            <th class="mobile-hide">Can Host</th>
          {/if}
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr class="me">
          <td>
            <Flag country_code={registration.player.country_code}/>
          </td>
          <td class="name">
            <PlayerName player={registration.player}/>
          </td>
          {#if tournament.mii_name_required}
            <td>{registration.player.mii_name}</td>
          {/if}
          <td class="mobile-hide">
            {#if registration.player.friend_codes.length > 0}
              {registration.player.friend_codes[0]}
            {/if}
          </td>
          {#if tournament.host_status_required}
            <td class="mobile-hide">{registration.player.can_host ? 'Yes' : 'No'}</td>
          {/if}
          <td>
            {#if check_registrations_open(tournament)}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                {#if tournament.require_single_fc || tournament.mii_name_required || tournament.host_status_required}
                <DropdownItem on:click={edit_reg_dialog.open}>
                  Edit
                </DropdownItem>
                {/if}
                <DropdownItem on:click={() => unregister(registration, tournament)}>
                  Unregister
                </DropdownItem>
              </Dropdown>
            {/if}
          </td>
        </tr>
      </tbody>
    </Table>
  {/if}
{/if}

<EditMyRegistration bind:this={edit_reg_dialog} {tournament} {friend_codes} {registration}/>

<style>
  col.country {
    width: 10%;
  }
  col.name {
    width: 25%;
  }
  col.mii-name {
    width: 25%;
  }
  col.friend-codes {
    width: 20%;
  }
  col.can-host {
    width: 10%;
  }
  col.actions {
    width: 10%;
  }
</style>
