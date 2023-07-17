<script lang="ts">
  import { onMount } from 'svelte';
  import TournamentPageItem from '$lib/components/TournamentPageItem.svelte';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';

  let tournaments: TournamentListItem[] = [];

  onMount(async () => {
    const res = await fetch('/api/tournaments/list');
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        tournaments.push(t);
      }
      tournaments = tournaments;
    }
  });
</script>

<h1>Tournaments</h1>
{#each tournaments as tournament}
  <TournamentPageItem {tournament} />
{/each}
