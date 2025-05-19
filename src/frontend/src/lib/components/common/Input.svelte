<script lang="ts">
    import Tooltip from "./Tooltip.svelte";
    import LL from "$i18n/i18n-svelte";
    export let name: string | null = null;
    export let minlength: number | null = null;
    export let maxlength: number | null = null;
    export let value: string | null = null;
    export let type: string | null = null;
    export let required = false;
    export let disabled = false;
    export let no_white_space = false;
    const pattern_exp = new RegExp(/^\S(?:.*\S)?$/);
</script>

<input {name} {minlength} {maxlength} bind:value={value} {...{type}} {required} {disabled} pattern={no_white_space ? pattern_exp.source : null}/>
{#if no_white_space && value && !pattern_exp.test(value)}
    <Tooltip is_warning>
        {$LL.COMMON.NO_SPACE_INPUT_WARNING()}
    </Tooltip>
{/if}