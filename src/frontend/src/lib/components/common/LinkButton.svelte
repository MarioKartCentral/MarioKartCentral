<script lang="ts">
  import Button from "./buttons/Button.svelte";

  export let href: string;
</script>

<!-- <a {href}><slot /></a> -->
<Button {href}><slot/></Button>

<style>
  a {
    text-decoration: none;
    color: white;
    transition: background-color 0.2s ease-in;
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    padding: 5px 10px;
  }
  a:hover {
    color: white;
    background-color: rgba(255, 255, 255, 0.4);
  }
</style>
