<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import Flag from '$lib/components/common/Flag.svelte';
  import FriendCodeDisplay from '$lib/components/common/FriendCodeDisplay.svelte';
  import { onMount } from 'svelte';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import CountrySelect from '$lib/components/common/CountrySelect.svelte';
  import FCTypeSelect from '$lib/components/common/FCTypeSelect.svelte';

  export let is_shadow: boolean | null = false;

  let players: PlayerInfo[] = [];
  let totalPlayers = 0;
  let totalPages = 0;
  let currentPage = 1;
  let filters: PlayerFilter = {
    fc_type: null,
    name: null,
    country: null,
    fc: null,
    name_or_fc: null,
    sort_by_newest: false,
  };

  async function fetchData() {
    players = [];
    let url = '/api/registry/players?detailed=true&is_banned=false&is_hidden=false';
    if (filters.fc_type != null && filters.fc_type != '') {
      url += '&fc_type=' + filters.fc_type;
    }
    if (filters.name_or_fc) {
      url += '&name_or_fc=' + filters.name_or_fc;
    }
    if (filters.country != null && filters.country != '') {
      url += '&country=' + filters.country;
    }
    if(is_shadow !== null) {
      url += `&is_shadow=${is_shadow}`;
    }
    if(filters.sort_by_newest) {
      url += `&sort_by_newest=${filters.sort_by_newest}`;
    }
    url += '&page=' + currentPage;
    console.log(url);
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      console.log(body);
      const body_players = body['player_list'];
      for (let t of body_players) {
        players.push(t);
      }
      players = players;
      totalPlayers = body['player_count'];
      totalPages = body['page_count'];
    }
  }

  async function search() {
    currentPage = 1;
    fetchData();
  }

  onMount(fetchData);
</script>

<form on:submit|preventDefault={search}>
  <div class="flex">
    <FCTypeSelect all_option hide_labels bind:type={filters.fc_type}/>
    <CountrySelect bind:value={filters.country} is_filter={true}/>
    <select bind:value={filters.sort_by_newest}>
      <option value={false}>{$LL.COMMON.SORT_BY_ALPHABETICAL()}</option>
      <option value={true}>{$LL.COMMON.SORT_BY_NEWEST()}</option>
    </select>
    <input class="search" bind:value={filters.name_or_fc} type="text" placeholder={$LL.PLAYERS.LIST.SEARCH_BY()} />
    <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
  </div>
</form>
<div class="player_list">
  {totalPlayers}
  {$LL.PLAYERS.PLAYERS()}
  <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
  {#if totalPlayers}
    <Table>
      <col class="country_code" />
      <col class="name" />
      <col class="friend_codes mobile-hide"/>
      <thead>
        <tr>
          <th></th>
          <th>{$LL.COMMON.NAME()}</th>
          <th class="mobile-hide">{$LL.FRIEND_CODES.FRIEND_CODES()}</th>
        </tr>
      </thead>
      <tbody>
        {#each players as player, i}
          <tr class="row-{i % 2}">
            <td><Flag country_code={player.country_code} /></td>
            <td>
              <a href="/{$page.params.lang}/registry/players/profile?id={player.id}" class={player.is_banned ? 'banned_name' : ''}>{player.name}</a>
            </td>
            <td class="mobile-hide">
              <FriendCodeDisplay friend_codes={player.friend_codes}/>
            </td>
          </tr>
        {/each}
      </tbody>
    </Table>
  {/if}
  <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
</div>


<style>
  col.country_code {
    width: 20%;
  }
  col.name {
    width: 40%;
  }
  col.friend_codes {
    width: 40%;
  }
  .banned_name {
    opacity: 0.7;
    text-decoration: line-through;
  }
  .flex {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 5px;
  }
  .player_list {
    margin-top: 10px;
  }
</style>
