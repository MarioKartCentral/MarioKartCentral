<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import RecruitingBadge from '$lib/components/badges/RecruitingBadge.svelte'
  import TagBadge from '$lib/components/badges/TagBadge.svelte';  
  import LL from '$i18n/i18n-svelte';

  export let team: Team;
</script>

<Table>
  <col class="tag" />
  <col class="name" />
  <col class="game" />
  <!-- <col class="recruiting" />
  <col class="mode" /> -->
  <thead>
    <tr>
      <th>{$LL.TEAM_LIST.TAG()}</th>
      <th>{$LL.TEAM_LIST.NAME()}</th>
      <th>{$LL.TEAM_LIST.STATUS()}</th>
    </tr>
  </thead>
  <tbody>
    {#each team.rosters as roster, i}
      <tr class="row-{i % 2}">
        <td>
          <TagBadge tag={team.tag} color={team.color} />
        </td>
        <td>
          {roster.name}
        </td>
        <td>     
          <GameBadge game={roster.game} />
          <ModeBadge mode={roster.mode} />
          <RecruitingBadge recruiting={roster.is_recruiting} />
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
    width: 45%;
  }
  /* col.recruiting {
    width: 25%;
  } */
  col.game {
    width: 40%;
  }
  /* col.mode {
    width: 15%;
  } */
</style>
