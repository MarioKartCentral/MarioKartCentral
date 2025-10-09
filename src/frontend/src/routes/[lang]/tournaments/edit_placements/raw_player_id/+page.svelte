<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import type { TournamentPlacementSimplePlayerIDs } from '$lib/types/tournament-placement';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

  let id = 0;
  let is_loaded = false;

  let text = '';

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    is_loaded = true;
  });

  async function savePlacements() {
    let conf = window.confirm($LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID_CONFIRM());
    if (!conf) return;
    let new_placements: TournamentPlacementSimplePlayerIDs[] = [];
    let lines = text.split('\n');
    for (let line of lines) {
      let vals = line.split(/[ \t]+/);
      if (vals.length < 2) {
        continue;
      }
      try {
        let reg_ids = vals.slice(0, vals.length - 1).map((p) => Number(p));
        if (!reg_ids.length) {
          alert($LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_LINE_INCORRECT({ line: line }));
          return;
        }
        let placement: number | null;
        let is_disqualified = false;
        let lower_bound: number | null = null;
        let description = null;
        if (vals[vals.length - 1].toUpperCase() === 'DQ') {
          placement = null;
          is_disqualified = true;
        } else {
          let range = vals[vals.length - 1].split('-');
          for (let n in range) {
            if (isNaN(Number(n))) {
              alert($LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_LINE_INCORRECT({ line: line }));
              return;
            }
          }
          if (range.length > 1) {
            lower_bound = Number(range[1]);
          }
          placement = Number(range[0]);
        }
        new_placements.push({
          player_ids: reg_ids,
          placement: placement,
          is_disqualified: is_disqualified,
          placement_lower_bound: lower_bound,
          placement_description: description,
        });
      } catch (e) {
        alert(`${$LL.TOURNAMENTS.PLACEMENTS.PARSE_TEXT_ERROR()}: ${e}`);
      }
    }

    const endpoint = `/api/tournaments/${id}/placements/setFromPlayerIDs`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(new_placements),
    });
    console.log(new_placements);
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.TOURNAMENTS.PLACEMENTS.SAVE_PLACEMENTS_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if is_loaded}
  <Section header={$LL.TOURNAMENTS.BACK_TO_TOURNAMENT()}>
    <div slot="header_content">
      <Button href="/{$page.params.lang}/tournaments/details?id={id}">{$LL.COMMON.BACK()}</Button>
    </div>
  </Section>
  <Section header="Placements Raw Input (Player IDs)">
    <div slot="header_content">
      <Button href="/{$page.params.lang}/tournaments/edit_placements?id={id}"
        >{$LL.TOURNAMENTS.PLACEMENTS.SWITCH_TO_INTERACTIVE_INPUT()}</Button
      >
      <Button href="/{$page.params.lang}/tournaments/edit_placements/raw?id={id}"
        >{$LL.TOURNAMENTS.PLACEMENTS.SWITCH_TO_RAW_INPUT()}</Button
      >
    </div>
    <div>
      {$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID_INSTRUCTIONS()}
    </div>
    <div>
      {$LL.TOURNAMENTS.PLACEMENTS.RAW_INPUT_PLAYER_ID_WARNING()}
    </div>
    <div>
      <textarea bind:value={text} />
    </div>
    <div>
      <Button on:click={savePlacements}>{$LL.COMMON.SAVE()}</Button>
    </div>
  </Section>
{/if}

<style>
  textarea {
    width: 90%;
    height: 500px;
    tab-size: 4;
  }
</style>
