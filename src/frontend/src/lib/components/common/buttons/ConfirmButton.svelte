<script lang="ts">
  import Button from './Button.svelte';
  import { CheckSolid } from 'flowbite-svelte-icons';
</script>

<Button circle={true} on:click>
  <CheckSolid class="w-4 h-4" />
</Button>
