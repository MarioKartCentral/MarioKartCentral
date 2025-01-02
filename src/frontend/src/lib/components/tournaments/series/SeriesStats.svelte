<script lang="ts">
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/Table.svelte';
  export let teams;
  let stats_mode = 'medals';
</script>

<div>
  <button on:click={() => (stats_mode = 'medals')}> Medals </button>
  <button on:click={() => (stats_mode = 'podiums')}> Podiums </button>
  <button on:click={() => (stats_mode = 'finals')}> Finals </button>
  <button on:click={() => (stats_mode = 'participations')}> Participations </button>
  <Table>
    <col class="placement" />
    <col class="team_tag" />
    <col class="team_name" />
    <col class="gold" />
    <col class="silver" />
    <thead><tr><th></th><th></th><th></th><th>👑</th><th>🥈</th><th>🥉</th></tr></thead>
    <col class="bronze" />
    {#each teams as team}
      <tr>
        {#if stats_mode === 'medals'}
          <td>{team.medals_placement}</td>
          <td><TagBadge tag={team.tag} color={1} /></td>
          <td>{team.name}</td>
          <td>{team.gold_medals}</td>
          <td>{team.silver_medals}</td>
          <td>{team.bronze_medals}</td>
        {/if}
        {#if stats_mode === 'podiums'}
          <td>{team.podiums_placement}</td>
          <td><TagBadge tag={team.tag} color={1} /></td>
          <td>{team.name}</td>
          <td>{team.podiums}</td>
        {/if}
        {#if stats_mode === 'finals'}
          <td>{team.finals_placement}</td>
          <td><TagBadge tag={team.tag} color={1} /></td>
          <td>{team.name}</td>
          <td>{team.finals}</td>
        {/if}
        {#if stats_mode === 'participations'}
          <td>{team.participations_placement}</td>
          <td><TagBadge tag={team.tag} color={1} /></td>
          <td>{team.name}</td>
          <td>{team.participations}</td>
        {/if}
      </tr>
    {/each}
  </Table>
</div>

<style></style>
