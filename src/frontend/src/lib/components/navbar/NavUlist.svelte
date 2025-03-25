<script lang="ts">
    import { NavUl } from "flowbite-svelte";

    export let min_desktop_px: number;
    export let menu_hidden: boolean;
</script>

<NavUl nonActiveClass='text-white font-bold' divClass='w-full min-[{min_desktop_px}px]:block min-[{min_desktop_px}px]:w-auto' bind:hidden={menu_hidden}
    ulClass='bg-primary-800 border-none flex flex-col p-4 mt-4 min-[{min_desktop_px}px]:flex-row min-[{min_desktop_px}px]:space-x-8 rtl:space-x-reverse min-[{min_desktop_px}px]:mt-0 min-[{min_desktop_px}px]:text-sm min-[{min_desktop_px}px]:font-medium'
    activeClass='text-white bg-primary-700 min-[{min_desktop_px}px]:bg-transparent min-[{min_desktop_px}px]:text-primary-700 min-[{min_desktop_px}px]:dark:text-white dark:bg-primary-600 min-[{min_desktop_px}px]:dark:bg-transparent'>
    <slot/>
</NavUl>