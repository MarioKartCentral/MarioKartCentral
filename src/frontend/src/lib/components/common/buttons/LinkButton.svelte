<script lang="ts">
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { LinkSolid } from 'flowbite-svelte-icons';

  export let href: string;
</script>

<Button size="lg" {href}>
  <LinkSolid class="mr-2" />
  <slot />
</Button>
