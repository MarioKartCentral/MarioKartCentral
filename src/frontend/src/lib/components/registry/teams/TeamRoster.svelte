<script lang="ts">
  import type { TeamRoster } from '$lib/types/team-roster';
  import Table from '$lib/components/common/Table.svelte';
  import { locale } from '$i18n/i18n-svelte';

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
  {roster.players.length} player{roster.players.length !== 1 ? 's' : ''}
  <Table>
    <col class="country" />
    <col class="name" />
    <col class="fc" />
    <col class="join_date" />
    <thead>
      <tr>
        <th />
        <th>Name</th>
        <th>Friend Code</th>
        <th>Join Date</th>
      </tr>
    </thead>
    <tbody>
      {#each roster.players as player}
        <tr>
          <td>{player.country_code}</td>
          <td>{player.name}</td>
          <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
          <td>{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
        </tr>
      {/each}
    </tbody>
  </Table>
</div>
