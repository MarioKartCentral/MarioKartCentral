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
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { game_fc_types } from '$lib/util/util';

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

  async function leaveRoster() {
    let conf = window.confirm($LL.TEAMS.PROFILE.LEAVE_ROSTER_CONFIRM({ roster_name: roster.name }));
    if (!conf) return;
    const payload = {
      roster_id: roster.id,
    };
    const endpoint = '/api/registry/teams/leave';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
      alert($LL.TEAMS.PROFILE.LEAVE_ROSTER_SUCCESS());
    } else {
      alert(`${$LL.TEAMS.PROFILE.LEAVE_ROSTER_FAILED()}: ${result['title']}`);
    }
  }
</script>

<div class="roster-container">
  <div class="roster-name">
    <TagBadge tag={roster.tag} color={roster.color} />
    {roster.name}
  </div>
  <div class="badges">
    <GameBadge game={roster.game} />
    <ModeBadge mode={roster.mode} />
  </div>
  {roster.players.length}
  {roster.players.length !== 1 ? $LL.TEAMS.PROFILE.PLAYERS() : $LL.TEAMS.PROFILE.PLAYER()}
  {#if roster.players.length}
    <Table>
      <col class="country" />
      <col class="name" />
      <col class="fc mobile-hide" />
      <col class="join_date mobile-hide" />
      <thead>
        <tr>
          <th></th>
          <th>{$LL.COMMON.NAME()}</th>
          <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODE()}</th>
          <th class="mobile-hide">{$LL.TEAMS.PROFILE.JOIN_DATE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each roster.players as player, i (player.player_id)}
          <tr class="row-{i % 2} {user_info.player_id === player.player_id ? 'me' : ''}">
            <td><Flag country_code={player.country_code} /></td>
            <td>
              <RosterPlayerName {player} />
            </td>
            <td class="mobile-hide">
              {#each player.friend_codes.filter((fc) => fc.type === game_fc_types[roster.game]) as fc, i (fc.id)}
                {#if i === 0}
                  {fc.fc}
                {/if}
              {/each}
            </td>
            <td class="mobile-hide">{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  {/if}
  {#if roster.players.find((r) => r.player_id === user_info.player_id)}
    <Button on:click={leaveRoster}>{$LL.TEAMS.PROFILE.LEAVE_ROSTER()}</Button>
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
  .banned_name {
    opacity: 0.7;
    text-decoration: line-through;
  }
</style>
