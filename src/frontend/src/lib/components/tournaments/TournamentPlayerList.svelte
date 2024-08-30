<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import Table from '$lib/components/common/Table.svelte';
  import Flag from '../common/Flag.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import PlayerName from './registration/PlayerName.svelte';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
    import { ChevronDownSolid } from 'flowbite-svelte-icons';
    import Dropdown from '../common/Dropdown.svelte';
    import DropdownItem from '../common/DropdownItem.svelte';
    import { unregister } from '$lib/util/util';

  export let tournament: Tournament;
  export let players: TournamentPlayer[];

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  export async function unregisterPlayer(player: TournamentPlayer) {
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
</script>

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
  {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations, tournament.id, tournament.series_id)}
    <col class="actions"/>
  {/if}
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
      {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations, tournament.id, tournament.series_id)}
        <th>Actions</th>
      {/if}
    </tr>
  </thead>
  <tbody>
    {#each players.filter((p) => !p.is_invite) as player, i}
      <tr class="row-{i % 2} {user_info.player?.id === player.player_id ? "me" : ""}">
        <td>
          <Flag country_code={player.country_code}/>
        </td>
        <td>
          <PlayerName {player}/>
        </td>
        {#if tournament.mii_name_required}
          <td>{player.mii_name}</td>
        {/if}
        <td class="mobile-hide">
          {#if player.friend_codes.length > 0}
            {player.friend_codes[0]}
          {/if}
        </td>
        {#if tournament.host_status_required}
          <td class="mobile-hide">{player.can_host ? 'Yes' : 'No'}</td>
        {/if}
        {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_registrations, tournament.id, tournament.series_id)}
          <td>
            <ChevronDownSolid class="cursor-pointer"/>
            <Dropdown>
              <DropdownItem on:click={() => unregisterPlayer(player)}>Remove</DropdownItem>
            </Dropdown>
          </td>
        {/if}
      </tr>
    {/each}
  </tbody>
</Table>

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
