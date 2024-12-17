<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import TournamentInfo from '$lib/components/tournaments/TournamentInfo.svelte';
  import MarkdownBox from '$lib/components/common/MarkdownBox.svelte';
  import TournamentRegistrations from '$lib/components/tournaments/TournamentRegistrations.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import type { Tournament } from '$lib/types/tournament';
  import TournamentRegisterPanel from '$lib/components/tournaments/registration/TournamentRegisterPanel.svelte';
  import PlacementsDisplay from '$lib/components/tournaments/placements/PlacementsDisplay.svelte';
  import Accordion from '$lib/components/common/Accordion.svelte';
  import AccordionItem from '$lib/components/common/AccordionItem.svelte';
  import LL from '$i18n/i18n-svelte';

  let id = 0;

  let tournament: Tournament;
  let not_found = false;
  $: tournament_name = tournament ? `${tournament.name}` : 'Tournaments';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/tournaments/${id}`);
    if (res.status !== 200) {
      not_found = true;
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
  <Section header={$LL.TOURNAMENTS.DETAILS()}>
    <Accordion>
      <AccordionItem open>
        <span slot="header">{$LL.TOURNAMENTS.DESCRIPTION()}</span>
        <MarkdownBox content={tournament.use_series_description ? String(tournament.series_description) : tournament.description} />
      </AccordionItem>
      <AccordionItem open>
        <span slot="header">{$LL.TOURNAMENTS.RULES()}</span>
        <MarkdownBox content={tournament.use_series_ruleset ? String(tournament.series_ruleset) : tournament.ruleset} />
      </AccordionItem>
    </Accordion>
  </Section>
  <PlacementsDisplay {tournament}/>
  <TournamentRegisterPanel {tournament} />
  <Section header={$LL.TOURNAMENTS.REGISTRATIONS.REGISTRATIONS()}>
    <TournamentRegistrations {tournament} />
  </Section>
{:else if not_found}
  {$LL.TOURNAMENTS.NOT_FOUND()}
{/if}
