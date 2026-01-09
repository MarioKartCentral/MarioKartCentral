<script context="module" lang="ts">
  let index: number = 0;
</script>

<script lang="ts">
  import { derived } from 'svelte/store';
  import { getContext } from 'svelte';
  import { ChevronSortOutline, ChevronDownOutline, ChevronUpOutline } from 'flowbite-svelte-icons';
  import type { TableHeaderSort } from './Table.svelte';
  export let sortable: boolean = false;
  export let active: boolean = false; // initial state
  export let onclick: (sortDirection: 'ascending' | 'descending') => void = () => null;

  const context = getContext<TableHeaderSort>('header-state');
  const colIndex = index++;

  const { activeSortIndex, sortDirection, toggleActive } = context;

  function handleClick() {
    // the sort order cycle is descending -> ascending -> descending
    toggleActive(colIndex);
    onclick($sortDirection);
  }

  if (active) {
    toggleActive(colIndex);
  }

  const icon = derived([activeSortIndex, sortDirection], ([$active, $sort]) => {
    if (colIndex !== $active) return ChevronSortOutline;
    switch ($sort) {
      case 'ascending':
        return ChevronUpOutline;
      case 'descending':
        return ChevronDownOutline
      default:
        return ChevronSortOutline;
    }
  });
</script>

<th aria-sort={colIndex === $activeSortIndex ? $sortDirection : undefined}>
  {#if sortable}
    <button on:click={handleClick}>
      <slot />
      <span aria-hidden="true">
        <svelte:component
          this={$icon}
          tabindex="-1"
          class="inline focus:outline-none"
        />
      </span>
    </button>
  {:else}
    <slot />
  {/if}
</th>
