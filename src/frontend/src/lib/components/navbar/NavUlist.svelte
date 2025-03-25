<script lang="ts">
    import { NavUl } from "flowbite-svelte";

    export let menu_hidden: boolean;
</script>

<NavUl nonActiveClass='text-white font-bold' divClass='w-full desktop:block desktop:w-auto' bind:hidden={menu_hidden}
    ulClass='bg-primary-800 border-none flex flex-col p-4 mt-4 desktop:flex-row desktop:space-x-8 rtl:space-x-reverse desktop:mt-0 desktop:text-sm desktop:font-medium'
    activeClass='text-white bg-primary-700 desktop:bg-transparent desktop:text-primary-700'>
    <slot/>
</NavUl>