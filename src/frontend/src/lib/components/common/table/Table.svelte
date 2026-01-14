<script context="module" lang="ts">
  export interface TableHeaderSort {
    activeSortIndex: Writable<number>;
    sortDirection: Writable<'ascending' | 'descending'>;
    toggleActive: (index: number) => void;
  }
</script>

<script lang="ts" generics="T">
  import { writable, type Writable } from 'svelte/store';
  import { setContext } from 'svelte';
  import { slide } from 'svelte/transition';
  import './table.css';
  export let containerClass: string = 'overflow-hidden rounded-[4px] m-[10px]';
  export let multiRow = false;
  export let data: T[];

  const activeSortIndex: Writable<number> = writable(-1);
  const activeSortDirection: Writable<'ascending' | 'descending'> = writable('descending');

  setContext<TableHeaderSort>('header-state', {
    get activeSortIndex() {
      return activeSortIndex;
    },
    get sortDirection() {
      return activeSortDirection;
    },
    toggleActive(index: number) {
      if (index === $activeSortIndex) {
        $activeSortDirection = $activeSortDirection === 'descending' ? 'ascending' : 'descending';
      } else {
        $activeSortIndex = index;
        $activeSortDirection = 'descending';
      }
    },
  });
</script>

<div class={containerClass} transition:slide={{ duration: 400 }}>
  <table data-multi-row={multiRow}>
    {#if $$slots.colgroup}
      <slot name="colgroup"></slot>
    {/if}

    {#if $$slots.header}
      <thead>
        <slot name="header"></slot>
      </thead>
    {/if}

    {#if multiRow}
      {#if $$slots.static}
        <tbody>
          <slot name="static" />
        </tbody>
      {/if}
      {#each data as item, idx (idx)}
        <tbody>
          <slot {item} {idx} />
        </tbody>
      {/each}
    {:else}
      <tbody>
        {#if $$slots.static}
          <slot name="static" />
        {/if}
        {#each data as item, idx (idx)}
          <slot {item} {idx} />
        {/each}
      </tbody>
    {/if}
    {#if $$slots.footer}
      <tfoot>
        <slot name="footer" />
      </tfoot>
    {/if}
  </table>
</div>
