<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import TournamentInfo from '$lib/components/tournaments/TournamentInfo.svelte';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import TournamentRegistrations from '$lib/components/tournaments/TournamentRegistrations.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import type { Tournament } from '$lib/types/tournament';

  let id = 0;
  let tournament_found = true;

  let tournament: Tournament;
  $: tournament_name = tournament ? `${tournament.tournament_name}` : 'Tournaments';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/tournaments/${id}`);
    if (res.status !== 200) {
      tournament_found = false;
      return;
    }
    const body: Tournament = await res.json();
    tournament = body;
  });
</script>

<svelte:head>
  <title>{tournament_name} | Mario Kart Central</title>
</svelte:head>

{#if tournament}
  <Section header="Tournament Info">
    <TournamentInfo {tournament} />
  </Section>
  <Section header="Tournament Details">
    <MarkdownBox content={tournament.description} />
  </Section>
  <Section header="Tournament Rules">
    <MarkdownBox content={tournament.ruleset} />
  </Section>
  <Section header="Tournament Registrations">
    <TournamentRegistrations {tournament} />
  </Section>
{/if}

<style>
  .container {
    width: 50%;
    margin: 20px auto 20px auto;
  }
</style>
