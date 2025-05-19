<script lang="ts">
    import { InfoCircleSolid, ExclamationCircleSolid } from "flowbite-svelte-icons";
    import { Tooltip } from "flowbite-svelte";

    export let style = "";
    export let is_warning = false;
</script>

<span class="tooltip" {style}>
    {#if is_warning}
        <ExclamationCircleSolid/>
    {:else}
        <InfoCircleSolid/>
    {/if}
</span>
<Tooltip>
    <slot/>
</Tooltip>

<style>
    .tooltip {
        margin-left: 5px;
    }
</style>