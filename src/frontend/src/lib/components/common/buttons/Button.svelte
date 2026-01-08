<script lang="ts">
  import { Button, Spinner } from 'flowbite-svelte';
  import LL from '$i18n/i18n-svelte';

  export let href: string | undefined = undefined;
  export let circle = false;
  export let type: 'submit' | 'button' | 'reset' | null | undefined = 'button';
  export let size: 'xs' | 'sm' | 'lg' | 'xl' | 'md' = 'sm';
  export let disabled = false;
  export let extra_classes = '';
  export let color:
    | 'red'
    | 'green'
    | 'blue'
    | 'yellow'
    | 'purple'
    | 'light'
    | 'dark'
    | 'primary'
    | 'alternative'
    | 'none'
    | undefined = undefined;
  export let working = false;
  export let ariaLabel: string | undefined = undefined;

  $: isLightColor = color === 'yellow' || color === 'light' || color === 'alternative' || color === 'none';
  $: hoverTextClass = isLightColor ? 'hover:text-gray-800' : 'hover:text-white';
</script>

<Button
  pill={circle}
  class="{extra_classes} {circle ? '!p-2' : ''} {hoverTextClass}"
  on:click
  {size}
  {href}
  {type}
  disabled={working || disabled}
  {color}
  aria-label={ariaLabel}
>
  {#if working}
    <div class="flex gap-2 items-center">
      <Spinner size="4" />
      {$LL.COMMON.WORKING()}
    </div>
  {:else}
    <slot />
  {/if}
</Button>
