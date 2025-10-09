<script lang="ts">
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { DiscordSolid } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';

  export let href: string;
</script>

<Button size="lg" color="blue" {href}>
  <DiscordSolid class="mr-2" />{$LL.LOUNGE.DISCORD_INVITE()}</Button
>
