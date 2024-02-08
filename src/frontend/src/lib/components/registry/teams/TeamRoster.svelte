<script lang="ts">
  import type { TeamRoster } from '$lib/types/team-roster';
  import Table from '$lib/components/common/Table.svelte';
  import { LL, locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
    import Flag from '$lib/components/common/Flag.svelte';

  export let roster: TeamRoster;

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };
</script>

<div>
  <h3>{roster.name}</h3>
  <h4>{roster.game}</h4>
  {roster.players.length}
  {roster.players.length !== 1 ? $LL.TEAM_PROFILE.PLAYERS() : $LL.TEAM_PROFILE.PLAYER()}
  {#if roster.players.length}
    <Table>
      <col class="country" />
      <col class="name" />
      <col class="fc" />
      <col class="join_date" />
      <thead>
        <tr>
          <th>{$LL.PLAYER_LIST.HEADER.COUNTRY()}</th>
          <th>{$LL.PLAYER_LIST.HEADER.NAME()}</th>
          <th>{$LL.PLAYER_PROFILE.FRIEND_CODE()}</th>
          <th>{$LL.TEAM_PROFILE.JOIN_DATE()}</th>
        </tr>
      </thead>
      <tbody>
        {#each roster.players as player}
          <tr>
            <td><Flag country_code={player.country_code}/></td>
            <td><a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}">{player.name}</a></td>
            <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
            <td>{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  {/if}
</div>
