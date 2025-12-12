<script lang="ts">
  import { Dropdown } from 'flowbite-svelte';

  export let placement: 'top' | 'bottom' | 'left' | 'right' = 'bottom';
  export let open = false;
  export let scroll = false;
</script>

<Dropdown class="bg-gray-600 text-white py-0 {scroll ? 'max-h-64 overflow-y-auto' : ''}" {placement} bind:open>
  <slot />
</Dropdown>
