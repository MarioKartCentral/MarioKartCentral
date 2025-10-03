<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import RecruitingBadge from '$lib/components/badges/RecruitingBadge.svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import LL from '$i18n/i18n-svelte';
  import { sortFilterRosters } from '$lib/util/util';
  import { page } from '$app/stores';

  export let team: Team;
</script>

<Table>
  <col class="tag" />
  <col class="name" />
  <col class="game" />
  <thead>
    <tr>
      <th>{$LL.COMMON.TAG()}</th>
      <th>{$LL.COMMON.NAME()}</th>
      <th>{$LL.TEAMS.LIST.STATUS()}</th>
    </tr>
  </thead>
  <tbody>
    {#each sortFilterRosters(team.rosters) as roster, i}
      <tr class="row-{i % 2}">
        <td>
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
            <TagBadge tag={roster.tag} color={roster.color} />
          </a>
        </td>
        <td>
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{roster.name}</a>
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
  col.game {
    width: 40%;
  }
</style>
