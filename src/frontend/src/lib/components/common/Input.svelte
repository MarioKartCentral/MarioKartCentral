<script lang="ts">
    export let name: string | null = null;
    export let id: string | null = null;
    export let minlength: number | null = null;
    export let maxlength: number | null = null;
    export let value: string | null = null;
    export let type: string = 'text';
    export let placeholder: string | null = null;
    export let required = false;
    export let disabled = false;
    export let no_white_space = false;
    export let pattern: string | null = null;
    export let title: string | null = null;

    const handleInput = (e: Event) => {
        const target = e.target as HTMLInputElement;
        value = target.value;
    };

    function trim_value() {
        if (no_white_space && value) {
            value = value.trim();
        }
    }
</script>

<input
    {id}
    {name}
    {minlength}
    {maxlength}
    {placeholder}
    value={value}
    type={type}
    {required}
    {disabled}
    {pattern}
    {title}
    on:input={handleInput}
    on:blur={trim_value}
/>