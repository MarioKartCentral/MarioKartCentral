<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import RecruitingBadge from '$lib/components/badges/RecruitingBadge.svelte'
  import Tag from '$lib/components/registry/teams/Tag.svelte';  
  import LL from '$i18n/i18n-svelte';

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
      <th>{$LL.TEAM_LIST.TAG()}</th>
      <th>{$LL.TEAM_LIST.NAME()}</th>
      <th>{$LL.TEAM_LIST.STATUS()}</th>
      <th>{$LL.TEAM_LIST.GAME()}</th>
      <th>{$LL.TEAM_LIST.MODE()}</th>
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
          <RecruitingBadge recruiting={roster.is_recruiting} />
        </td>
        <td>
          <GameBadge game={roster.game} />
        </td>
        <td>
          <ModeBadge mode={roster.mode} />
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
