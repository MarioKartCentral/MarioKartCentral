<script lang="ts">
  import type { Team, TeamList } from '$lib/types/team';
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
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';

  let teams: Team[] = [];

  let show_rosters: { [id: number]: boolean } = {};
  let totalTeams = 0;
  let totalPages = 0;

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
    name_or_tag: string | null;
    is_historical: boolean;
    is_active: boolean | null;
    min_player_count: number | null;
    sort_by_newest: boolean;
    page: number;
  }

  let filters: TeamFilter = {
    game: null,
    mode: null,
    name_or_tag: null,
    is_historical: false,
    is_active: null,
    sort_by_newest: false,
    min_player_count: null,
    page: 1,
  }

  const min_players = 6;
  let active_historical_filter = "min_players";
  $: {
    if(active_historical_filter === "min_players") {
      filters.min_player_count = min_players;
      filters.is_historical = false;
    }
    else if (active_historical_filter === "active") {
      filters.min_player_count = null;
      filters.is_historical = false;
    }
    else {
      filters.min_player_count = null;
      filters.is_historical = true;
    }
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
      const body: TeamList = await res.json();
      for (let t of body.teams) {
        teams.push(t);
      }
      teams = teams;
      totalTeams = body.team_count;
      totalPages = body.page_count;
    }
  }

  async function search() {
    filters.page = 1;
    await fetchData();
  }

  onMount(async () => {
    await fetchData();
  });
</script>

<form on:submit|preventDefault={search}>
  <div class="flex">
    <div class="option">
      <GameModeSelect all_option hide_labels inline is_team bind:game={filters.game} bind:mode={filters.mode}/>
    </div>
    <div class="option">
      <input class="search" bind:value={filters.name_or_tag} type="text" placeholder={$LL.TEAMS.LIST.SEARCH_BY()}/>
    </div>
    <div class="option">
      <select bind:value={active_historical_filter}>
        <option value="min_players">{$LL.TEAMS.LIST.ACTIVE_TEAMS_MIN_PLAYERS({count: min_players})}</option>
        <option value="active">{$LL.TEAMS.LIST.ACTIVE_TEAMS()}</option>
        <option value="historical">{$LL.TEAMS.LIST.HISTORICAL_TEAMS()}</option>
      </select>
    </div>
    <div class="option">
      <select bind:value={filters.sort_by_newest}>
        <option value={false}>{$LL.COMMON.SORT_BY_ALPHABETICAL()}</option>
        <option value={true}>{$LL.COMMON.SORT_BY_NEWEST()}</option>
      </select>
    </div>
    <div class="option">
      <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
    </div>
  </div>
</form>
{$LL.TEAMS.LIST.TEAM_COUNT({count: totalTeams})}
<PageNavigation bind:currentPage={filters.page} bind:totalPages={totalPages} refresh_function={fetchData}/>
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
        <tr class="inner">
          <td colspan="10">
            <RosterList {team} />
          </td>
        </tr>
      {/if}
    {/each}
  </tbody>
</Table>
<PageNavigation bind:currentPage={filters.page} bind:totalPages={totalPages} refresh_function={fetchData}/>

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
    gap: 5px;
  }
  input {
    width: 250px;
  }
</style>