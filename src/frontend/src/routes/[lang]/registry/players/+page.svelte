<script lang="ts">
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import GameSelect from '$lib/components/common/GameSelect.svelte';
  import CountrySelect from '$lib/components/common/CountrySelect.svelte';

  let players: PlayerInfo[] = [];
  let totalPlayers = 0;
  let totalPages = 0;
  let currentPage = 1;
  let oldPage = 1;
  let filters: PlayerFilter = {
    game: null,
    name: null,
    country: null,
    fc: null,
    name_or_fc: null,
  };

  async function fetchData() {
    players = [];
    let url = '/api/registry/players?detailed=true';
    if (filters.game != null && filters.game != '') {
      url += '&game=' + filters.game;
    }
    if (filters.name_or_fc) {
      url += '&name_or_fc=' + filters.name_or_fc;
    }
    if (filters.country != null && filters.country != '') {
      url += '&country=' + filters.country;
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

  $: {
    if (currentPage != oldPage) {
      oldPage = currentPage;
      fetchData();
    }
  }
  onMount(fetchData);
</script>

<Section header={$LL.PLAYER_LIST.PLAYER_LISTING()}>
  <form on:submit|preventDefault={fetchData}>
    <div class="flex">
      <GameSelect all_option hide_labels bind:game={filters.game}/>
      <CountrySelect bind:value={filters.country} is_filter={true}/>
      <input class="search" bind:value={filters.name_or_fc} type="text" placeholder={$LL.PLAYER_LIST.FILTERS.SEARCH_BY()} />
      <Button type="submit">{$LL.PLAYER_LIST.SEARCH()}</Button>
    </div>
  </form>
  <div class="player_list">
    {totalPlayers}
    {$LL.PLAYER_LIST.PLAYERS()}
    <PageNavigation bind:currentPage={currentPage} bind:totalPages={totalPages} refresh_function={fetchData}/>
    <PlayerList {players}/>
  </div>
  
</Section>

<style>
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