<script lang="ts">
  import { onMount } from 'svelte';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamList from '$lib/components/registry/teams/TeamList.svelte';

  let teams: Team[] = [];

  onMount(async () => {
    const res = await fetch('/api/registry/teams');
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        teams.push(t);
      }
      teams = teams;
    }
  });
</script>

<Section header="Team Listing">
  {teams.length} teams
  <TeamList {teams} />
</Section>

<style>
</style>
