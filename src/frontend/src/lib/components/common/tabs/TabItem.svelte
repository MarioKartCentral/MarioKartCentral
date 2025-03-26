<script lang="ts">
    import { TabItem } from "flowbite-svelte";

    export let title: string;
    export let open = false;
</script>

<TabItem {open} {title}>
    <slot/>
</TabItem>