<script lang="ts">
  import { onMount } from 'svelte';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';

  let players: PlayerInfo[] = [];

  onMount(async () => {
    const res = await fetch('/api/registry/players?detailed=true');
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        players.push(t);
      }
      players = players;
      console.log('players : ', players);
    }
  });
</script>

<Section header="Player Listing">
  {players.length} players
  <PlayerList {players} />
</Section>
