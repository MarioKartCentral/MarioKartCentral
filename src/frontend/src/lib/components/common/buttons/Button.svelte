<script lang="ts">
  import { Button } from 'flowbite-svelte';

  export let href: string | undefined = undefined;
  export let circle = false;
  export let type: 'submit' | 'button' | 'reset' | null | undefined = 'button';
  export let size: 'xs' | 'sm' | 'lg' | 'xl' | 'md' = 'sm';
  export let disabled = false;
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
</script>

<Button pill={circle} class={circle ? '!p-2' : ''} on:click {size} {href} {type} {disabled} {color}>
  <slot />
</Button>

<style>
  .button {
    background-color: theme('colors.primary.500');
  }
</style>
