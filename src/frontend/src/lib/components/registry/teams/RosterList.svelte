<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';

  export let team: Team;
</script>

<Table>
  <col class="tag" />
  <col class="name" />
  <col class="game" />
  <col class="recruiting" />
  <col class="mode" />
  <thead>
    <tr>
      <th>Tag</th>
      <th>Name</th>
      <th>Status</th>
      <th>Game</th>
      <th>Mode</th>
    </tr>
  </thead>
  <tbody>
    {#each team.rosters as roster, i}
      <tr class="row-{i % 2}">
        <td>
          {roster.tag}
        </td>
        <td>
          {roster.name}
        </td>
        <td>
          {roster.is_recruiting ? 'Recruiting' : 'Not Recruiting'}
        </td>
        <td>
          {roster.game}
        </td>
        <td>
          {roster.mode}
        </td>
      </tr>
    {/each}
  </tbody>
</Table>

<style>
  col.tag {
    width: 15%;
  }
  col.name {
    width: 30%;
  }
  col.recruiting {
    width: 25%;
  }
  col.game {
    width: 15%;
  }
  col.mode {
    width: 15%;
  }
</style>
