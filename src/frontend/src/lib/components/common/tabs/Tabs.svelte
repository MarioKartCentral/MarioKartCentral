<script lang="ts">
    import { Tabs } from "flowbite-svelte";
</script>

<Tabs tabStyle="full" defaultClass="flex rounded-lg shadow-sm" contentClass='p-4 rounded-lg bg-gray-700 mt-4' 
    activeClasses='p-4 w-full focus:outline-hidden bg-gray-800 text-white'
    inactiveClasses='p-4 w-full text-gray-400 focus:outline-hidden hover:text-white bg-gray-700 hover:bg-gray-800'>
    <slot/>
</Tabs>