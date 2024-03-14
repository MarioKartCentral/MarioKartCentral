<script lang="ts">
    import { Dropdown } from "flowbite-svelte";

    export let placement: "top"|"bottom"|"left"|"right"="bottom";
</script>

<Dropdown class="bg-gray-600 text-white" {placement}>
    <slot/>
</Dropdown>