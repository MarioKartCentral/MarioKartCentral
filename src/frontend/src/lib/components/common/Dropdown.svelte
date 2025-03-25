<script lang="ts">
    import { Dropdown } from "flowbite-svelte";

    export let placement: "top"|"bottom"|"left"|"right"="bottom";
    export let open = false;
</script>

<Dropdown class="bg-gray-600 text-white" {placement} bind:open>
    <slot/>
</Dropdown>