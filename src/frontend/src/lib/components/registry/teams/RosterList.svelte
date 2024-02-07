<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import Tag from '$lib/components/registry/teams/Tag.svelte';

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
          <Tag {team} />
        </td>
        <td>
          {roster.name}
        </td>
        <td>
          <Badge
            classId={roster.is_recruiting ? 'recruiting' : 'not_recruiting'}
            value={roster.is_recruiting ? 'Recruiting' : 'Not Recruiting'}
          />
        </td>
        <td>
          <Badge classId={'game_' + roster.game} value={roster.game.toUpperCase()} />
        </td>
        <td>
          <Badge classId={'mode_' + roster.mode} value={roster.mode} />
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
