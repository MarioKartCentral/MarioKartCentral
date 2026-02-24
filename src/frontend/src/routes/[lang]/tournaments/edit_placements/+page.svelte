<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import PlacementsDragDropZone from '$lib/components/tournaments/placements/PlacementsDragDropZone.svelte';
  import type { TournamentPlacementList } from '$lib/types/tournament-placement';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import { check_tournament_permission, tournament_permissions } from '$lib/util/permissions';
  import { user } from '$lib/stores/stores';

  let tournamentId: number;
  let placements: TournamentPlacementList;
  let isLoaded = false;

  onMount(async () => {
    let paramId = $page.url.searchParams.get('id');
    tournamentId = parseInt(paramId || '');
    if (tournamentId) {
      const response = await fetch(`/api/tournaments/${tournamentId}/placements`);
      if (response.ok) {
        placements = await response.json();
      }
    }
    isLoaded = true;
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

{#if isLoaded}
  {#if placements && check_tournament_permission($user, tournament_permissions.manage_placements, placements.tournament_id)}
    <Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
      <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/details?id={placements.tournament_id}"
          >{$LL.COMMON.BACK()}</Button
        >
      </div>
    </Section>
    <Section header={$LL.TOURNAMENTS.PLACEMENTS.EDIT_PLACEMENTS()}>
      <div slot="header_content">
        <Button href="/{$page.params.lang}/tournaments/edit_placements/raw?id={placements.tournament_id}">
          {$LL.TOURNAMENTS.PLACEMENTS.SWITCH_TO_RAW_INPUT()}
        </Button>
        <Button href="/{$page.params.lang}/tournaments/edit_placements/raw_player_id?id={placements.tournament_id}">
          {$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID()}
        </Button>
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
  {:else if placements}
    {$LL.COMMON.NO_PERMISSION()}
  {:else}
    {$LL.TOURNAMENTS.NOT_FOUND()}
  {/if}
{/if}
