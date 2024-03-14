<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import type { TournamentPlayer } from '$lib/types/tournament-player';
  import Table from '$lib/components/common/Table.svelte';
    import Flag from '../common/Flag.svelte';
    import CaptainBadge from '../badges/CaptainBadge.svelte';
    import type { UserInfo } from '$lib/types/user-info';
    import { user } from '$lib/stores/stores';
    import PlayerName from './registration/PlayerName.svelte';

  export let tournament: Tournament;
  export let players: TournamentPlayer[];

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });
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
      </tr>
    {/each}
  </tbody>
</Table>

<style>
  col.country {
    width: 10%;
  }
  col.name {
    width: 30%;
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
</style>
