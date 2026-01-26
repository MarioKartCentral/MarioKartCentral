<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Table from '$lib/components/common/table/Table.svelte';
  import TableHeader from '$lib/components/common/table/TableHeader.svelte';
  import { page } from '$app/stores';
  import Flag from '$lib/components/common/Flag.svelte';
  import FriendCodeDisplay from '$lib/components/common/FriendCodeDisplay.svelte';
  import { onMount } from 'svelte';
  import { locale } from '$i18n/i18n-svelte';
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
    sort_by: null,
  };

  async function fetchData() {
    let url = '/api/registry/players?detailed=true&is_banned=false&is_hidden=false&matching_fcs_only=true';
    if (filters.fc_type != null && filters.fc_type != '') {
      url += '&fc_type=' + filters.fc_type;
    }
    if (filters.name_or_fc) {
      url += '&name_or_fc=' + filters.name_or_fc;
    }
    if (filters.country != null && filters.country != '') {
      url += '&country=' + filters.country;
    }
    if (is_shadow !== null) {
      url += `&is_shadow=${is_shadow}`;
    }
    if (filters.sort_by) {
      url += `&sort_by=${filters.sort_by}`;
    }
    url += '&page=' + currentPage;
    const res = await fetch(url);
    if (!res.ok) {
      players = [];
      return;
    }
    const { player_list, player_count, page_count } = await res.json();
    players = player_list;
    totalPlayers = player_count;
    totalPages = page_count;
  }

  async function search() {
    currentPage = 1;
    fetchData();
  }

  onMount(fetchData);

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };
</script>

<form on:submit|preventDefault={search}>
  <div class="flex">
    <FCTypeSelect all_option hide_labels bind:type={filters.fc_type} />
    <CountrySelect bind:value={filters.country} is_filter={true} />
    <select class="sm:hidden" bind:value={filters.sort_by} on:change={search}>
      <option value="name">{$LL.COMMON.SORT_BY_ALPHABETICAL()} (A-Z)</option>
      <option value="-name">{$LL.COMMON.SORT_BY_ALPHABETICAL()} (Z-A)</option>
      <option value="-join_date">{$LL.COMMON.SORT_BY_NEWEST()}</option>
      <option value="join_date">{$LL.COMMON.SORT_BY_OLDEST()}</option>
    </select>
    <input class="search" bind:value={filters.name_or_fc} type="text" placeholder={$LL.PLAYERS.LIST.SEARCH_BY()} />
    <Button type="submit">{$LL.COMMON.SEARCH()}</Button>
  </div>
</form>
<div class="player_list">
  {totalPlayers}
  {$LL.PLAYERS.PLAYERS()}
  <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
  {#if totalPlayers}
    <Table data={players} let:item={player} bind:sortKey={filters.sort_by}>
      <colgroup slot="colgroup">
        <col class="country_code" />
        <col class="name" />
        <col class="friend_codes mobile-hide" />
        <col class="registration-date hidden sm:table-column" />
      </colgroup>
      <tr slot="header">
        <TableHeader />
        <TableHeader sortable active sortKey="name" onclick={search}>
          {$LL.COMMON.NAME()}
        </TableHeader>
        <TableHeader classes="mobile-hide">
          {$LL.FRIEND_CODES.FRIEND_CODES()}
        </TableHeader>
        <TableHeader
          sortable
          direction="descending"
          sortKey="join_date"
          classes="hidden sm:table-cell"
          onclick={search}
        >
          {$LL.PLAYERS.PROFILE.REGISTRATION_DATE()}
        </TableHeader>
      </tr>
      <tr class="row">
        <td><Flag country_code={player.country_code} /></td>
        <td>
          <a
            href="/{$page.params.lang}/registry/players/profile?id={player.id}"
            class={player.is_banned ? 'banned_name' : ''}>{player.name}</a
          >
        </td>
        <td class="mobile-hide">
          <FriendCodeDisplay friend_codes={player.friend_codes} />
        </td>
        <td class="hidden sm:table-cell">
          {new Intl.DateTimeFormat($locale, options).format(player.join_date * 1000)}
        </td>
      </tr>
    </Table>
  {/if}
  <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
</div>

<style>
  col.country_code {
    width: 1%;
  }
  col.name {
    width: 39%;
  }
  col.friend_codes {
    width: 30%;
  }
  col.registration-date {
    width: 30%;
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
