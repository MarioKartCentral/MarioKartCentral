<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import RosterList from '$lib/components/registry/teams/RosterList.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';

  export let teams: Team[];

  let show_rosters: { [id: number]: boolean } = {};

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour12: true,
  };

  function toggle_show_rosters(team_id: number) {
    show_rosters[team_id] = !show_rosters[team_id];
  }
</script>

<Table>
  <col class="tag" />
  <col class="name" />
  <col class="rosters" />
  <col class="registration_date" />
  <thead>
    <tr>
      <th>{$LL.TEAM_LIST.TAG()}</th>
      <th>{$LL.TEAM_LIST.NAME()}</th>
      <th>{$LL.TEAM_LIST.ROSTERS()}</th>
      <th>{$LL.TEAM_LIST.REGISTERED()}</th>
    </tr>
  </thead>
  <tbody>
    {#each teams as team, i}
      <tr class="row-{i % 2}">
        <td>
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}"> <TagBadge tag={team.tag} color={team.color}/> </a>
        </td>
        <td>
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a>
        </td>
        <td>
          {team.rosters.length}
          <button class="show-hide" on:click={() => toggle_show_rosters(team.id)}>
            ({show_rosters[team.id] ? $LL.TEAM_LIST.HIDE() : $LL.TEAM_LIST.SHOW()})
          </button>
        </td>
        <td>
          {new Date(team.creation_date * 1000).toLocaleString($locale, options)}
        </td>
      </tr>
      {#if show_rosters[team.id]}
        <tr class="row-{i % 2}">
          <td colspan="10">
            <RosterList {team} />
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</Table>

<style>
  col.tag {
    width: 15%;
  }
  col.name {
    width: 35%;
  }
  col.rosters {
    width: 20%;
  }
  col.registration_date {
    width: 30%;
  }
  button.show-hide {
    background-color: transparent;
    border: none;
    color: white;
    cursor: pointer;
  }
</style>
