<script lang="ts">
    import { Accordion } from "flowbite-svelte";
</script>

<Accordion multiple defaultClass="text-white" activeClass="bg-primary-700" inactiveClass="bg-primary-800">
    <slot/>
</Accordion>