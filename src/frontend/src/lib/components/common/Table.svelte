<script lang="ts">
  import { slide } from 'svelte/transition';

  export let show_padding = true;
</script>

<div class={show_padding ? 'container' : ''} transition:slide={{ duration: 400 }}>
  <table>
    <slot />
  </table>
</div>

<style>
  .container {
    padding: 10px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: small;
    text-align: left;
    word-break: break-word;
  }
  table :global(thead) {
    background-color: theme('colors.primary.800');
  }
  table :global(tr) {
    border-top: 1px solid rgb(0, 128, 0, 0.5);
  }
  
  table :global(th) {
    padding: 5px 10px;
  }
  table :global(td) {
    padding: 10px;
    text-align: left;
  }
  /* Alternating row background colors: in an each block,
        put the class name as row-{i%2} */
  table :global(tr) {
    background-color: rgba(235, 255, 255, 0.15);
  }
  table :global(tr.row-1) {
    background-color: rgba(235, 255, 255, 0.1);
  }
  table :global(tr.inner) {
    background-color: rgba(235, 255, 255, 0.05);
  }
  /* Style for a table row containing the logged in user */
  table :global(tr.me) {
    background-color: theme('colors.primary.200'/ 30%) ;
  }

  @media(max-width: 1024px) {
    table :global(.mobile-hide) {
      display: none;
    }
  }
  
</style>
