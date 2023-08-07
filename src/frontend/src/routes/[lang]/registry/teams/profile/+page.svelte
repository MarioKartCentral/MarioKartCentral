<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import TeamProfile from '$lib/components/registry/teams/TeamProfile.svelte';
  import TeamRoster from '$lib/components/registry/teams/TeamRoster.svelte';

  let id = 0;
  let team: Team;
  $: team_name = team ? team.name : 'Registry';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/registry/teams/${id}`);
    if (res.status != 200) {
      return;
    }
    const body: Team = await res.json();
    team = body;
  });
</script>

<svelte:head>
  <title>{team_name} | Mario Kart Central</title>
</svelte:head>

{#if team}
  <Section header="Team Profile">
    <TeamProfile {team} />
  </Section>
  <Section header="Rosters">
    {#each team.rosters as roster}
      <TeamRoster {roster} />
    {/each}
  </Section>
{/if}
