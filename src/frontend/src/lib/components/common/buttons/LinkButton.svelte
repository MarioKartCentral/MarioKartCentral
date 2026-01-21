<script lang="ts">
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { LinkOutline } from 'flowbite-svelte-icons';

  export let href: string;
</script>

<Button size="lg" {href}>
  <LinkOutline class="mr-2" />
  <slot />
</Button>
