<script lang="ts">
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';
  import PlayerFilter from '$lib/components/registry/players/PlayerFilter.svelte';

  let players: PlayerInfo[] = [];
  let totalPages: number = 0;
  let currentPage: number = 1;
  let oldPage: number = 1;
  let filters = {
    game: null,
    name: null,
    country: null,
    fc: null,
  };

  async function fetchData() {
    players = [];
    let url = '/api/registry/players?detailed=true';
    if (filters.game != null && filters.game != '') {
      url += '&game=' + filters.game;
    }
    if (filters.name != null && filters.name != '') {
      url += '&name=' + filters.name;
    }
    if (filters.country != null && filters.country != '') {
      url += '&country=' + filters.country;
    }
    url += '&page=' + currentPage;
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      console.log(body);
      const body_players = body[0];
      for (let t of body_players) {
        players.push(t);
      }
      players = players;
      totalPages = body[1];
    }
  }

  $: {
    if (filters.game != null || filters.name != null || filters.country != null || currentPage != oldPage) {
      oldPage = currentPage;
      fetchData();
    }
  }
  onMount(fetchData);
</script>

<Section header="Player Listing">
  <PlayerFilter bind:filters />
  {players.length} players
  <PlayerList {players} {totalPages} bind:currentPage />
</Section>
