<script lang="ts">
    export let name: string | null = null;
    export let minlength: number | null = null;
    export let maxlength: number | null = null;
    export let value: string | null = null;
    export let type: string | null = null;
    export let placeholder: string | null = null;
    export let required = false;
    export let disabled = false;
    export let no_white_space = false;

    function trim_value() {
        if(no_white_space && value) {
            value = value.trim();
        }
    }
</script>

<input {name} {minlength} {maxlength} {placeholder} bind:value={value} {...{type}} {required} {disabled} on:blur={trim_value} on:input/>