<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import PlacementsDragDropZone from '$lib/components/tournaments/placements/PlacementsDragDropZone.svelte';
  import type { TournamentPlacementList } from '$lib/types/tournament-placement';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

  let id = 0;
  let placements: TournamentPlacementList;
  let is_loaded = false;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);

    const res = await fetch(`/api/tournaments/${id}/placements`);
    let placements_body: TournamentPlacementList = await res.json();
    placements = placements_body;
    is_loaded = true;
  });

  function reset_placements() {
    let conf = window.confirm('Are you sure you want to reset placements? You will lose all of your progress.');
    if (!conf) return;
    for (let p of placements.placements) {
      p.placement = null;
      p.is_disqualified = false;
      p.placement_description = null;
      p.placement_lower_bound = null;
      placements.unplaced.push(p);
    }
    placements.placements = [];
    placements.unplaced = placements.unplaced;
    placements = placements;
  }
</script>

{#if is_loaded}
  <Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
    <div slot="header_content">
      <Button href="/{$page.params.lang}/tournaments/details?id={placements.tournament_id}">{$LL.COMMON.BACK()}</Button>
    </div>
  </Section>
  <Section header={$LL.TOURNAMENTS.PLACEMENTS.EDIT_PLACEMENTS()}>
    <div slot="header_content">
      <Button href="/{$page.params.lang}/tournaments/edit_placements/raw?id={placements.tournament_id}"
        >{$LL.TOURNAMENTS.PLACEMENTS.SWITCH_TO_RAW_INPUT()}</Button
      >
      <Button href="/{$page.params.lang}/tournaments/edit_placements/raw_player_id?id={id}"
        >{$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID()}</Button
      >
      <Button on:click={reset_placements}>Reset</Button>
    </div>
    {#key placements.placements}
      <PlacementsDragDropZone tournament_id={placements.tournament_id} placements={placements.placements} />
    {/key}
  </Section>
  <Section header={$LL.TOURNAMENTS.PLACEMENTS.UNPLACED({ is_squad: true })}>
    {#key placements.unplaced}
      <PlacementsDragDropZone
        tournament_id={placements.tournament_id}
        placements={placements.unplaced}
        is_placements={false}
      />
    {/key}
  </Section>
{/if}
