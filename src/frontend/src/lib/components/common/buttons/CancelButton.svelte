<script lang="ts">
  import Button from './Button.svelte';
  import { CloseSolid } from 'flowbite-svelte-icons';
  export let ariaLabel: string | undefined = undefined;
</script>

<Button circle={true} on:click {ariaLabel}>
  <CloseSolid class="w-4 h-4" />
</Button>
