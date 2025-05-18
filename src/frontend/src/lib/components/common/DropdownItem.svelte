<script lang="ts">
    import { DropdownItem } from 'flowbite-svelte';

    export let href: string | undefined = undefined;
    export let target: string | undefined = undefined;
</script>

<DropdownItem {href} {target} class="hover:bg-primary-700" on:click>
    <slot/>
</DropdownItem>

