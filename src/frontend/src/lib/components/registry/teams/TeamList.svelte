<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Table from '$lib/components/common/Table.svelte';
  import RosterList from '$lib/components/registry/teams/RosterList.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { sortFilterRosters } from '$lib/util/util';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { onMount } from 'svelte';

  let teams: Team[] = [];

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

  type TeamFilter = {
    game: string | null;
    mode: string | null;
    name: string | null;
    is_historical: boolean;
    is_active: boolean | null;
  }

  let filters: TeamFilter = {
    game: null,
    mode: null,
    name: null,
    is_historical: false,
    is_active: null,
  }

  async function fetchData() {
    teams = [];
    let url = '/api/registry/teams?';
    let filter_strings = [];
    if(filters.is_historical) {
      filters.is_active = null;
    }
    else {
      filters.is_active = true;
    }
    for(const [key, value] of Object.entries(filters)) {
      if(value !== null) {
        filter_strings.push(`${key}=${value}`);
      }
    }
    url += filter_strings.join("&");
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        teams.push(t);
      }
      teams = teams;
    }
  }

  onMount(async () => {
    fetchData();
  });
</script>

<form on:submit|preventDefault={fetchData}>
  <div class="flex">
    <div class="option">
      <GameModeSelect all_option hide_labels inline bind:game={filters.game} bind:mode={filters.mode}/>
    </div>
    <div class="option">
      <input class="search" bind:value={filters.name} type="text" placeholder={$LL.TEAMS.LIST.SEARCH_BY()}/>
    </div>
    <div class="option">
      <select bind:value={filters.is_historical}>
        <option value={false}>{$LL.TEAMS.LIST.ACTIVE_TEAMS()}</option>
        <option value={true}>{$LL.TEAMS.LIST.HISTORICAL_TEAMS()}</option>
      </select>
    </div>
    <div class="option">
      <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
    </div>
  </div>
</form>
{$LL.TEAMS.LIST.TEAM_COUNT({count: teams.length})}
<Table>
  <col class="tag" />
  <col class="name" />
  <col class="rosters" />
  <col class="registration_date" />
  <thead>
    <tr>
      <th>{$LL.COMMON.TAG()}</th>
      <th>{$LL.COMMON.NAME()}</th>
      <th>{$LL.TEAMS.LIST.ROSTERS()}</th>
      <th>{$LL.TEAMS.LIST.REGISTERED()}</th>
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
          {sortFilterRosters(team.rosters).length}
          <button class="show-hide" on:click={() => toggle_show_rosters(team.id)}>
            {show_rosters[team.id] ? $LL.COMMON.HIDE_BUTTON() : $LL.COMMON.SHOW_BUTTON()}
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
  .flex {
    width: 100%;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  .option {
    margin-right: 10px;
  }
  input {
    width: 250px;
  }
</style>