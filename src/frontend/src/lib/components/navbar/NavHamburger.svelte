<script lang="ts">
    import { twMerge } from 'tailwind-merge';
    import { ToolbarButton } from 'flowbite-svelte';
    import NavHamburgerIcon from '$lib/components/navbar/NavHamburgerIcon.svelte';

    export let menu_hidden: boolean;
    export let title = 'Open main menu';
    
    let btnClass: string = `ms-3 desktop:hidden hover:bg-gray-500 focus:outline-none focus:ring-0`;
  </script>
  
  <ToolbarButton name={title} on:click={() => menu_hidden = !menu_hidden} {...$$restProps} class={twMerge(btnClass, $$props.class)}>
    <NavHamburgerIcon class='h-6 w-6 shrink-0 text-white outline-none' />
  </ToolbarButton>