<script lang="ts">
  import { getContext } from 'svelte';
  import { twMerge } from 'tailwind-merge';
  import type { NavbarLiType } from 'flowbite-svelte/NavUl.svelte';
  import { ChevronDownOutline } from 'flowbite-svelte-icons';
  import { page } from '$app/stores';

  export let nav_name = '';
  export let has_dropdown = false;
  export let href: string = '';
  export let activeClass: string | undefined = undefined;
  export let nonActiveClass: string | undefined = undefined;

  const context = getContext<NavbarLiType>('navbarContext') ?? {};
  const activeUrlStore = getContext('activeUrl') as { subscribe: (callback: (value: string) => void) => void };

  let navUrl = '';
  activeUrlStore.subscribe((value) => {
    navUrl = value;
  });

  $: active = navUrl ? href === navUrl : false;

  $: liClass = twMerge(
    `text-white block py-2 pe-4 ps-3 desktop:p-0 rounded-sm desktop:border-0`,
    active ? (activeClass ?? context.activeClass) : (nonActiveClass ?? context.nonActiveClass),
    $$props.class,
    has_dropdown ? 'cursor-pointer' : '',
  );
</script>

<li class="w-max">
  <svelte:element
    this={href ? 'a' : 'div'}
    role={href ? 'link' : 'presentation'}
    {href}
    {...$$restProps}
    on:blur
    on:change
    on:click
    on:focus
    on:keydown
    on:keypress
    on:keyup
    on:mouseenter
    on:mouseleave
    on:mouseover
    class={liClass}
    class:active={$page.data.activeNavItem === nav_name}
  >
    <span><slot /></span>
    {#if has_dropdown}
      <ChevronDownOutline class="inline" />
    {/if}
  </svelte:element>
</li>

<style>
  @media (width >= 1100px) {
    span {
      position: relative;
      height: 100%;
    }

    .active > span::after {
      position: absolute;
      background-color: white;
      content: '';
      height: 3px;
      border-radius: 3px;
      inset: auto 0 -6px 0;
    }
  }
</style>
