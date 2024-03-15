<script lang="ts">
    import TagBadge from "../badges/TagBadge.svelte";
    import { colors } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";

    export let tag: string | null = "";
    export let color = 0;
    export let name = "color"

</script>

<select {name} bind:value={color}>
    {#each colors as c, i}
        <option value={i}>{$LL.COLORS[c.label]()}</option>
    {/each}
</select>
<TagBadge {tag} {color}/>