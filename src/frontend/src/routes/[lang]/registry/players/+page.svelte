<script lang="ts">
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';
  import PlayerFilter from '$lib/components/registry/players/PlayerFilter.svelte';

  let players: PlayerInfo[] = [];
  let filters = {
    game: null,
    name: null,
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
    const res = await fetch(url);
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        players.push(t);
      }
      players = players;
    }
  }

  $: {
    if (filters.game != null || filters.name != null) {
      fetchData();
    }
  }

  onMount(fetchData);
</script>

<Section header="Player Listing">
  <PlayerFilter bind:filters />
  {players.length} players
  <PlayerList {players} />
</Section>
