<script lang="ts">
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

<input {name} {minlength} {maxlength} {value} {type} {required} {disabled} pattern={no_white_space ? pattern_exp.source : null}/>