<script lang="ts">
  import type { PlacementOrganizer } from '$lib/types/placement-organizer';
  import SquadPlacementDisplay from './SquadPlacementDisplay.svelte';
  import { createEventDispatcher } from 'svelte';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import { ChevronDownOutline } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import { twMerge } from 'tailwind-merge';

  const dispatch = createEventDispatcher<{ dq: null; placement_change: null }>();

  export let placement: PlacementOrganizer;
  export let is_edit: boolean;
  export let is_homepage = false;
  export let extraClasses: string = '';

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
  $: classes = twMerge(bg_class, extraClasses);
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

<tr class={classes}>
  <td class="rank w-[50px]">
    {getPlacementText(placement)}
  </td>
  <td class="sm:table-cell w-[10ch]" class:hidden={!placement.squad.name && placement.squad.players.length <= 4}>
    {#if placement.squad.tag}
      <TagBadge tag={placement.squad.tag} color={placement.squad.color} />
    {/if}
  </td>
  <td>
    <SquadPlacementDisplay {placement} />
  </td>
  <td class="flex gap-2 {is_homepage ? 'hidden' : ''}">
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
      {/if}
    {/if}
  </td>
  {#if is_edit}
    <td>
      <div class="actions">
        {$LL.COMMON.ACTIONS()}
        <ChevronDownOutline />
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
    </td>
  {/if}
</tr>

<style>
  .gold {
    background-color: rgba(255, 254, 149, 0.3);
    color: #fffab0;
  }

  .silver {
    background-color: rgba(195, 255, 255, 0.3);
    color: #dcfffc;
  }

  .bronze {
    background-color: rgba(255, 158, 110, 0.3);
    color: #ffcbae;
  }

  .other {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .dq {
    background-color: rgba(255, 0, 0, 0.2);
  }

  .pointer {
    cursor: pointer;
  }

  .rank {
    text-align: center;
    font-size: 1.5em;
    font-weight: 600;
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

  input.placement-num {
    width: 50px;
    height: 36px;
  }
</style>
