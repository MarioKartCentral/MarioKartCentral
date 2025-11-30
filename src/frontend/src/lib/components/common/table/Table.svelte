<script lang="ts" generics="T">
  import { slide } from 'svelte/transition';
  import './table.css';
  export let containerClass: string = 'overflow-hidden rounded-[4px] m-[10px]';
  export let multiRow = false;
  export let data: T[];
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

<style>
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: small;
    text-align: left;
    word-break: break-word;
  }
  thead {
    background-color: #3c7b53;
  }
</style>
