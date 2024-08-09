<script lang="ts">
  import type { TeamRoster } from '$lib/types/team-roster';
  import Table from '$lib/components/common/Table.svelte';
  import { LL, locale } from '$i18n/i18n-svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import RosterPlayerName from './RosterPlayerName.svelte';

  export let roster: TeamRoster;

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };
</script>

<div class="roster-container">
  <div class="roster-name">
    {roster.name}
  </div>
  <div class="badges">
    <GameBadge game={roster.game}/>
    <ModeBadge mode={roster.mode}/>
  </div>
  {roster.players.length}
  {roster.players.length !== 1 ? $LL.TEAM_PROFILE.PLAYERS() : $LL.TEAM_PROFILE.PLAYER()}
  {#if roster.players.length}
    <Table>
      <col class="country" />
      <col class="name" />
      <col class="fc mobile-hide" />
      <col class="join_date mobile-hide" />
      <thead>
        <tr>
          <th></th>
          <th>{$LL.PLAYER_LIST.HEADER.NAME()}</th>
          <th class="mobile-hide">{$LL.PLAYER_PROFILE.FRIEND_CODE()}</th>
          <th class="mobile-hide">{$LL.TEAM_PROFILE.JOIN_DATE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each roster.players as player, i}
          <tr class="row-{i % 2} {user_info.player_id === player.player_id ? 'me' : ''}">
            <td><Flag country_code={player.country_code} /></td>
            <td>
              <RosterPlayerName {player}/>
            </td>
            <td class="mobile-hide">{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
            <td class="mobile-hide">{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  {/if}
</div>

<style>
  div.roster-name {
    font-size: 1.17em;
    font-weight: bold;
  }
  div.badges {
    margin-top: 5px;
    margin-bottom: 5px;
  }
  div.roster-container {
    margin-bottom: 20px;
  }
  col.country {
    width: 10%;
  }
  col.name {
    width: 30%;
  }
  col.fc {
    width: 30%;
  }
  col.join_date {
    width: 30%;
  }
</style>
