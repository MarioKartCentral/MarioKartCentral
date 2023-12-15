<script lang="ts">
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';
  import PlayerFilterOptions from '$lib/components/registry/players/PlayerFilterOptions.svelte';
  import type { PlayerFilter } from '$lib/types/registry/players/player-filter';

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
    name_or_fc: null
  }

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
      const body_players = body["player_list"];
      for (let t of body_players) {
        players.push(t);
      }
      players = players;
      totalPlayers = body["player_count"];
      totalPages = body["page_count"];
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

<Section header="Player Listing">
  <form on:submit|preventDefault={fetchData}>
    <PlayerFilterOptions bind:filters />
    <button type="submit">Search</button>
  </form>
  {totalPlayers} players
  <PlayerList {players} {totalPages} bind:currentPage />
</Section>
