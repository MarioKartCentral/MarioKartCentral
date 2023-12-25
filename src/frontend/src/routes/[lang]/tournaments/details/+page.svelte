<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import TournamentInfo from '$lib/components/tournaments/TournamentInfo.svelte';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import TournamentRegistrations from '$lib/components/tournaments/TournamentRegistrations.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import type { Tournament } from '$lib/types/tournament';
  import { setSeriesPerms, addPermission, permissions } from '$lib/util/util';
  import TournamentRegisterPanel from '$lib/components/tournaments/registration/TournamentRegisterPanel.svelte';

  let id = 0;

  let tournament: Tournament;
  $: tournament_name = tournament ? `${tournament.tournament_name}` : 'Tournaments';

  setSeriesPerms();
  addPermission(permissions.edit_tournament);

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/tournaments/${id}`);
    if (res.status !== 200) {
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
  <TournamentInfo {tournament} />
  <Section header="Tournament Details">
    <MarkdownBox content={tournament.description} />
  </Section>
  <Section header="Tournament Rules">
    <MarkdownBox content={tournament.ruleset} />
  </Section>
  <TournamentRegisterPanel {tournament} />
  <Section header="Tournament Registrations">
    <TournamentRegistrations {tournament} />
  </Section>
{/if}
