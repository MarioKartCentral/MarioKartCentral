<script lang="ts">
  import { slide } from 'svelte/transition';
</script>

<div class="container" transition:slide={{ duration: 400 }}>
  <table>
    <slot />
  </table>
</div>

<style>
  .container {
    padding: 10px;
  }
  table {
    background-color: rgba(255, 255, 255, 0.15);
    border-collapse: collapse;
    width: 100%;
  }
  table :global(thead) {
    background-color: rgb(0, 128, 0, 0.6);
  }
  table :global(tr) {
    border-top: 1px solid rgb(0, 128, 0, 0.5);
  }
  table :global(td) {
    padding: 10px;
    text-align: center;
  }
  /* Alternating row background colors: in an each block,
        put the class name as row-{i%2} */
  table :global(tr.row-1) {
    background-color: rgba(255, 255, 255, 0.1);
  }
</style>
