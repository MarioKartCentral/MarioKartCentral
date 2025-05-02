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
</script>

<Button pill={circle} class="{extra_classes} {circle ? '!p-2' : ''} hover:text-white" on:click {size} {href} {type} disabled={working || disabled} {color}>
  {#if working}
    <div class="flex gap-2 items-center">
      <Spinner size=4/>
      {$LL.COMMON.WORKING()}
    </div>
  {:else}
    <slot />
  {/if}
</Button>
