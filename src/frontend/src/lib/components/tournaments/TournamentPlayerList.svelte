<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import Table from '$lib/components/common/Table.svelte';
  import Flag from '../common/Flag.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import PlayerName from './registration/PlayerName.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import Dropdown from '../common/Dropdown.svelte';
  import DropdownItem from '../common/DropdownItem.svelte';
  import { check_registrations_open } from '$lib/util/util';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import EditPlayerRegistration from './registration/EditPlayerRegistration.svelte';
  import FriendCodeDisplay from '../common/FriendCodeDisplay.svelte';

  export let tournament: Tournament;
  export let players: TournamentPlayer[];
  export let is_privileged = false;
  export let my_player: TournamentPlayer | null = null;
  export let exclude_invites = true;

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let edit_reg_dialog: EditPlayerRegistration;

  function get_players() {
    if(!exclude_invites) {
      return players;
    }
    return players.filter((p) => !p.is_invite);
  }

  async function unregisterPlayer(player: TournamentPlayer) {
    const conf = window.confirm(`Are you sure you would like to unregister ${player.name} from this tournament?`);
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: player.squad_id,
      player_id: player.player_id
    };
    console.log(payload);
    const endpoint = `/api/tournaments/${tournament.id}/forceUnregister`;
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

  async function kickPlayer(player: TournamentPlayer) {
    let conf = window.confirm('Are you sure you would like to kick this player?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: player.squad_id,
      player_id: player.player_id,
    };
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
      alert(`Kicking player failed: ${result['title']}`);
    }
  }

  async function makeCaptain(player: TournamentPlayer) {
    let conf = window.confirm('Are you sure you would like to transfer captain permissions to this player?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: player.squad_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/makeCaptain`;
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
      alert(`Transferring captain permissions failed: ${result['title']}`);
    }
  }

  async function addRepresentative(player: TournamentPlayer) {
    const payload = {
      squad_id: player.squad_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/addRepresentative`;
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
      alert(`Adding representative failed: ${result['title']}`);
    }
  }

  async function removeRepresentative(player: TournamentPlayer) {
    const payload = {
      squad_id: player.squad_id,
      player_id: player.player_id,
    };
    const endpoint = `/api/tournaments/${tournament.id}/removeRepresentative`;
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
      alert(`Adding representative failed: ${result['title']}`);
    }
  }

  async function unregister() {
    if (!my_player) {
      return;
    }
    if (my_player.is_squad_captain) {
      alert('Please unregister this squad or set another player as captain before unregistering for this tournament');
      return;
    }
    const conf = window.confirm('Are you sure you would like to unregister for this tournament?');
    if (!conf) {
      return;
    }
    const payload = {
      squad_id: my_player.squad_id,
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

<Table>
  <col class="country" />
  <col class="name" />
  {#if tournament.mii_name_required && exclude_invites}
    <col class="mii-name" />
  {/if}
  <col class="friend-codes mobile-hide" />
  {#if tournament.host_status_required && exclude_invites}
    <col class="can-host mobile-hide" />
  {/if}
  {#if is_privileged || my_player}
    <col class="actions"/>
  {/if}
  <thead>
    <tr>
      <th />
      <th>Name</th>
      {#if tournament.mii_name_required && exclude_invites}
        <th>In-Game Name</th>
      {/if}
      <th class="mobile-hide">Friend Codes</th>
      {#if tournament.host_status_required && exclude_invites}
        <th class="mobile-hide">Can Host</th>
      {/if}
      {#if is_privileged || my_player}
        <th>Actions</th>
      {/if}
    </tr>
  </thead>
  <tbody>
    {#each get_players() as player, i}
      <tr class="row-{i % 2} {user_info.player?.id === player.player_id ? "me" : ""}">
        <td>
          <Flag country_code={player.country_code}/>
        </td>
        <td>
          <PlayerName player_id={player.player_id} name={player.name} is_squad_captain={player.is_squad_captain} is_representative={player.is_representative}
          is_bagger_clause={player.is_bagger_clause}/>
        </td>
        {#if tournament.mii_name_required && exclude_invites}
          <td>{player.mii_name}</td>
        {/if}
        <td class="mobile-hide">
          {#if player.friend_codes.length > 0}
            <FriendCodeDisplay friend_codes={player.friend_codes} selected_fc_id={player.selected_fc_id}/>
          {/if}
        </td>
        {#if tournament.host_status_required && exclude_invites}
          <td class="mobile-hide">{player.can_host ? 'Yes' : 'No'}</td>
        {/if}
        
        {#if is_privileged || my_player}
          <td>
            {#if is_privileged}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                <DropdownItem on:click={() => edit_reg_dialog.open(player, true)}>Edit</DropdownItem>
                <DropdownItem on:click={() => unregisterPlayer(player)}>Remove</DropdownItem>
              </Dropdown>
            {:else if my_player?.player_id === player.player_id && check_registrations_open(tournament)}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                {#if check_tournament_permission(user_info, tournament_permissions.register_tournament, tournament.id, tournament.series_id, true) &&
                  (tournament.require_single_fc || tournament.mii_name_required || tournament.host_status_required)}
                  <DropdownItem on:click={() => edit_reg_dialog.open(player)}>Edit</DropdownItem>
                {/if}
                <DropdownItem on:click={unregister}>Unregister</DropdownItem>
              </Dropdown>
            {:else if my_player?.is_squad_captain && my_player?.squad_id === player.squad_id && check_registrations_open(tournament)}
              <ChevronDownSolid class="cursor-pointer"/>
              <Dropdown>
                <DropdownItem on:click={() => kickPlayer(player)}>
                  {player.is_invite ? "Retract Invite" : "Kick"}
                </DropdownItem>
                {#if !player.is_invite}
                  <DropdownItem on:click={() => makeCaptain(player)}>Make Captain</DropdownItem>
                  {#if tournament.teams_only}
                    {#if !player.is_representative}
                      <DropdownItem on:click={() => addRepresentative(player)}>Make Representative</DropdownItem>
                    {:else}
                      <DropdownItem on:click={() => removeRepresentative(player)}>Remove Representative</DropdownItem>
                    {/if}
                  {/if}
                {/if}
              </Dropdown>
            {/if}
          </td>
          
        {/if}
        
      </tr>
    {/each}
  </tbody>
</Table>

<EditPlayerRegistration bind:this={edit_reg_dialog} {tournament}/>

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
