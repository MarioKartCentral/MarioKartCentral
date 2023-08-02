<script lang="ts">
  import { onMount } from 'svelte';
  import TournamentPageItem from '$lib/components/tournaments/TournamentPageItem.svelte';
  import type { TournamentListItem } from '$lib/types/tournament-list-item';
  import Section from '$lib/components/common/Section.svelte';

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

<Section header="Tournaments">
  {#each tournaments as tournament}
    <TournamentPageItem {tournament} />
  {/each}
</Section>

