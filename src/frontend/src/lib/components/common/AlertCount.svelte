<script lang="ts">
    import { Indicator } from "flowbite-svelte";
    import type { IndicatorPlacementType } from "flowbite-svelte";

    export let count: number;
    export let placement: IndicatorPlacementType | undefined = undefined;
</script>

<Indicator color="red" size="lg" border-size="xl" {placement}>
    <span class="text-white text-xs font-bold">{count}</span>
</Indicator>