<script lang="ts">
  import { derived } from 'svelte/store';
  import { getContext } from 'svelte';
  import { CaretSortSolid, CaretDownSolid, CaretUpSolid } from 'flowbite-svelte-icons';
  import type { TableHeaderSort } from './Table.svelte';
  export let sortable: boolean = false;
  export let active: boolean = false; // initial state
  export let direction: 'ascending' | 'descending' = 'ascending'
  export let classes: string = '';
  export let sortKey: string | null = null
  export let onclick: (sortDirection: 'ascending' | 'descending') => void = () => null;

  const context = getContext<TableHeaderSort>('header-state');
  const { activeSortKey, sortDirection, toggleActive } = context;

  function handleClick() {
    toggleActive(sortKey, direction);
    onclick($sortDirection);
  }

  if (active) {
    toggleActive(sortKey, direction);
  }

  const icon = derived([activeSortKey, sortDirection], ([$active, $sort]) => {
    if (sortKey !== $active) return CaretSortSolid;
    switch ($sort) {
      case 'ascending':
        return CaretUpSolid;
      case 'descending':
        return CaretDownSolid;
      default:
        return CaretSortSolid;
    }
  });
</script>

<th class={classes} aria-sort={sortKey === $activeSortKey ? $sortDirection : undefined} data-key={sortKey ?? undefined}>
  {#if sortable}
    <button on:click={handleClick}>
      <slot />
      <span aria-hidden="true">
        <svelte:component this={$icon} tabindex="-1" class="inline focus:outline-none" size="sm"/>
      </span>
    </button>
  {:else}
    <slot />
  {/if}
</th>
