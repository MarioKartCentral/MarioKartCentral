<script lang="ts">
    import { Indicator } from "flowbite-svelte";
    import type { IndicatorPlacementType } from "flowbite-svelte";

    export let count: number;
    export let limit = 99; // will display as "99+" if count > 99
    export let placement: IndicatorPlacementType | undefined = undefined;

    $: countText = count > limit ? `${limit}+` : `${count}`;
    $: countClass = countText.length > 1 ? "w-fit px-1" : ""
</script>

<Indicator color="red" size="lg" border-size="xl" {placement} class={countClass}>
    <span class="text-white text-xs font-bold">{countText}</span>
</Indicator>