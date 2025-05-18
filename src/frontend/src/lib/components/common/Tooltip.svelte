<script lang="ts">
    import { InfoCircleSolid } from "flowbite-svelte-icons";
    import { Tooltip } from "flowbite-svelte";
</script>

<span class="tooltip">
    <InfoCircleSolid/>
</span>
<Tooltip>
    <slot/>
</Tooltip>

<style>
    .tooltip {
        margin-left: 5px;
    }
</style>