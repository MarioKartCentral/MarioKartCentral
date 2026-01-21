<script lang="ts">
  import Button from './Button.svelte';
  import { CheckOutline } from 'flowbite-svelte-icons';
</script>

<Button circle={true} on:click>
  <CheckOutline class="w-4 h-4" />
</Button>
