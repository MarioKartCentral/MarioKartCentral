<script lang="ts">
    import { getContext } from 'svelte';
    import { twMerge } from 'tailwind-merge';
    import type { NavbarLiType } from 'flowbite-svelte/NavUl.svelte';
    import { page } from '$app/stores';
  
    export let min_desktop_px: number;
    export let nav_name = "";
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

    function checkSelectedNav(name: string) {
        if($page.data.activeNavItem === name) {
            return "text-white font-bold underline underline-offset-4";
        }
        return "";
    }
  
    $: active = navUrl ? href === navUrl : false;
  
    $: liClass = twMerge(`block py-2 pe-4 ps-3 min-[${min_desktop_px}px]:p-0 rounded-sm min-[${min_desktop_px}px]:border-0`, 
        active ? activeClass ?? context.activeClass : nonActiveClass ?? context.nonActiveClass, $$props.class,
        has_dropdown ? "cursor-pointer" : "", checkSelectedNav(nav_name));
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
    >
      <slot />
    </svelte:element>
  </li>