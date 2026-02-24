<script context="module" lang="ts">
  export interface TableHeaderSort {
    activeSortKey: Readable<string | null>;
    sortDirection: Readable<'ascending' | 'descending'>;
    toggleActive: (key: string | null, initalDirection: 'ascending' | 'descending') => void;
  }
</script>

<script lang="ts" generics="T">
  import { derived, writable, type Writable, type Readable } from 'svelte/store';
  import { setContext } from 'svelte';
  import { slide } from 'svelte/transition';
  import './table.css';
  export let containerClass: string = 'overflow-hidden rounded-[4px] m-[10px]';
  export let multiRow = false;
  export let data: T[];
  export let sortKey: string | null = null;

  const sortKeyStore: Writable<string | null> = writable(sortKey);
  $: $sortKeyStore = sortKey;
  const activeKey: Readable<string | null> = derived(sortKeyStore, ($key) => {
    if (!$key) return null;
    return $key.startsWith('-') ? $key.slice(1) : $key;
  });
  const activeSortDirection: Readable<'ascending' | 'descending'> = derived(sortKeyStore, ($key) => {
    return $key?.startsWith('-') ? 'descending' : 'ascending';
  });

  setContext<TableHeaderSort>('header-state', {
    get activeSortKey() {
      return activeKey;
    },
    get sortDirection() {
      return activeSortDirection;
    },
    toggleActive(key: string | null, initialDirection: 'ascending' | 'descending') {
      if (key === $activeKey) {
        sortKey = $activeSortDirection === 'ascending' ? `-${key}` : key;
      } else {
        sortKey = initialDirection === 'descending' ? `-${key}` : key;
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
