<script lang="ts">
  import type { PlacementOrganizer } from '$lib/types/placement-organizer';
  import SquadPlacementDisplay from './SquadPlacementDisplay.svelte';
  import { createEventDispatcher } from 'svelte';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import { ChevronDownSolid } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';

  const dispatch = createEventDispatcher<{ dq: null; placement_change: null }>();

  export let placement: PlacementOrganizer;
  export let is_edit: boolean;
  export let is_homepage = false;

  let saved_placement = placement.placement;

  let bg_class = 'other';
  $: {
    bg_class = 'other';
    if (placement.is_disqualified) {
      bg_class = 'dq';
    } else if (placement.placement === 1) {
      bg_class = 'gold';
    } else if (placement.placement === 2) {
      bg_class = 'silver';
    } else if (placement.placement === 3) {
      bg_class = 'bronze';
    }
  }
  function getPlacementChar(num: number | null) {
    if (num === null) {
      return '-';
    }
    if (num === 1) {
      return '👑';
    }
    if (num === 2) {
      return '🥈';
    }
    if (num === 3) {
      return '🥉';
    }
    return num;
  }

  function getPlacementText(placement: PlacementOrganizer) {
    if (placement.is_disqualified) {
      return 'DQ';
    }
    let text = getPlacementChar(placement.placement);
    if (placement.placement_lower_bound) {
      text += ' - ' + getPlacementChar(placement.placement_lower_bound);
    }
    return text;
  }

  function toggleDQ() {
    placement.is_disqualified = !placement.is_disqualified;
    if (placement.is_disqualified) {
      placement.placement = null;
      placement.bounded = false;
      placement.placement_lower_bound = null;
      placement.tie = false;
    }
    dispatch('dq');
  }

  function editPlacement() {
    if (placement.placement === null || placement.placement < 1) {
      placement.placement = saved_placement;
    }
    placement.is_disqualified = false;
    placement.bounded = false;
    placement.placement_lower_bound = null;
    placement.tie = false;
    saved_placement = placement.placement;
    dispatch('placement_change');
  }
</script>

<div class="flex {bg_class}">
  <div class="rank {is_homepage ? 'rank-homepage' : 'rank-tournament-page'}">
    {getPlacementText(placement)}
  </div>
  <div class="info">
    <SquadPlacementDisplay squad={placement.squad} />
  </div>

  <div class="description {is_homepage ? 'hidden' : ''}">
    {#if placement.placement !== null}
      {#if is_edit}
        <input
          class="title"
          bind:value={placement.description}
          placeholder={$LL.TOURNAMENTS.PLACEMENTS.PLACEMENT_TITLE()}
          maxlength="32"
        />
        {#if placement.placement !== null}
          <input
            class="placement-num"
            type="number"
            bind:value={placement.placement}
            on:blur={editPlacement}
            minlength="1"
          />
        {/if}
      {:else if placement.description}
        {placement.description}
      {/if}
    {/if}
  </div>
  {#if is_edit}
    <div class="actions">
      {$LL.COMMON.ACTIONS()}
      <ChevronDownSolid />
    </div>
    <Dropdown>
      <DropdownItem>
        <label for="tie">{$LL.TOURNAMENTS.PLACEMENTS.TIE()}</label>
        <input id="tie" type="checkbox" bind:checked={placement.tie} on:change />
      </DropdownItem>
      <DropdownItem>
        <label for="bound">{$LL.TOURNAMENTS.PLACEMENTS.LOWER_BOUND()}</label>
        <input id="bound" type="checkbox" bind:checked={placement.bounded} on:change />
      </DropdownItem>
      <DropdownItem on:click={toggleDQ}>
        {$LL.TOURNAMENTS.PLACEMENTS.TOGGLE_DQ()}
      </DropdownItem>
    </Dropdown>
  {/if}
</div>

<style>
  div.flex {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 5px;
    font-size: 80%;
  }
  div.flex:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  div.gold {
    background-color: rgba(255, 254, 149, 0.3);
    color: #fffab0;
  }
  div.silver {
    background-color: rgba(195, 255, 255, 0.3);
    color: #dcfffc;
  }
  div.bronze {
    background-color: rgba(255, 158, 110, 0.3);
    color: #ffcbae;
  }
  div.other {
    background-color: rgba(255, 255, 255, 0.1);
  }
  div.dq {
    background-color: rgba(255, 0, 0, 0.2);
  }
  .pointer {
    cursor: pointer;
  }
  .rank {
    display: block;
    text-align: center;
    font-size: 1.5em;
    font-weight: 600;
  }
  .rank-homepage {
    width: 50px;
  }
  .rank-tournament-page {
    width: 75px;
    @media (max-width: 600px) {
      width: 50px;
    }
  }
  .info {
    min-width: 150px;
    max-width: 400px;
  }
  .actions {
    display: flex;
    width: 100px;
    gap: 5px;
    cursor: pointer;
    padding: 5px;
  }
  input.title {
    width: 150px;
    height: 36px;
  }
  div.description {
    display: flex;
    gap: 5px;
    align-items: center;
  }
  input.placement-num {
    width: 50px;
    height: 36px;
  }
</style>
