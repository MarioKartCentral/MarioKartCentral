<script lang="ts">
    import { Tabs } from "flowbite-svelte";
</script>

<Tabs tabStyle="full" defaultClass="flex rounded-lg shadow-sm" contentClass='p-4 bg-gray-700' 
    activeClasses='p-4 w-full focus:outline-hidden bg-gray-700 text-white'
    inactiveClasses='p-4 w-full text-gray-400 focus:outline-hidden hover:text-white bg-gray-600 hover:bg-gray-700'>
    <slot/>
</Tabs>