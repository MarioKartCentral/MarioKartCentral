<script lang="ts">
    import TagBadge from "../badges/TagBadge.svelte";
    import { colors } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";

    export let tag: string | null = "";
    export let color = 0;
    export let name = "color"

    let sorted_colors = colors.toSorted((a, b) => a.label.localeCompare(b.label));

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const color_strings: any = $LL.COLORS;
</script>

<div class="color-select">
    <select {name} bind:value={color}>
        {#each sorted_colors as c}
            <option value={c.id}>{color_strings[c.label]()}</option>
        {/each}
    </select>
    <TagBadge {tag} {color}/>
</div>

<style>
    .color-select {
        display: flex;
        gap: 10px;
        align-items: center;
    }
</style>