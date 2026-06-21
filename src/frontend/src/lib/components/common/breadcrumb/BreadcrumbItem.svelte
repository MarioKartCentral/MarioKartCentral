<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { ChevronLeftOutline, ChevronRightOutline, HomeSolid } from 'flowbite-svelte-icons';
  import { twMerge } from 'tailwind-merge';

  export let home: boolean = false;
  export let href: string | undefined = undefined;
  export let returnText: string | undefined = undefined;
  export let truncate: boolean = true;
  export let current: boolean = false;

  const tag = href ? 'a' : 'span';

  type ChevronProps = {
    'aria-hidden': boolean;
    tabindex: number;
    size: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  };

  const chevronProps: ChevronProps = {
    'aria-hidden': true,
    tabindex: -1,
    size: 'xl',
  };

  const truncateLiClasses = truncate ? 'max-w-[350px]' : '';
  const truncateInnerClasses = truncate ? 'overflow-hidden text-ellipsis' : '';
</script>

<li class={truncateLiClasses}>
  {#if !home}
    <span class="mx-2 shrink-0 text-gray-100 hidden sm:inline">
      <ChevronRightOutline {...chevronProps} />
    </span>
  {/if}
  <svelte:element
    this={tag}
    aria-current={current ? 'page' : undefined}
    class={twMerge('item-inner', truncateInnerClasses)}
    {href}
  >
    {#if home}
      <HomeSolid ariaLabel={$LL.NAVBAR.HOME_PAGE()} />
    {:else}
      <span class="me-2 shrink-0 bg-primary-700 rounded-[50%] sm:hidden">
        <ChevronLeftOutline {...chevronProps} color="white" />
      </span>
    {/if}
    {#if returnText}
      <span class={twMerge('sm:hidden', truncateInnerClasses)}>{returnText}</span>
      <span class="hidden sm:inline"><slot /></span>
    {:else}
      <span><slot /></span>
    {/if}
  </svelte:element>
</li>

<style>
  li {
    list-style-type: none;
    flex-shrink: 0;
    display: none;
    white-space: nowrap;
    align-items: center;
  }

  li:last-child {
    color: white;
  }

  li:nth-last-child(2) {
    display: flex;
    font-weight: 600;
  }

  a[aria-current='page'],
  span[aria-current='page'] {
    font-weight: 600;
  }

  .item-inner {
    display: flex;
    align-items: center;
  }

  @media (min-width: 640px) {
    li {
      display: flex;
    }

    li:nth-last-child(2) {
      font-weight: revert-layer;
    }

    li:not(:last-child) {
      color: oklch(92.8% 0.006 264.531);
    }

    .item-inner {
      display: revert-layer;
      align-items: unset;
    }
  }
</style>
