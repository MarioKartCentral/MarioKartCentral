<script lang="ts">
    import { DropdownItem } from 'flowbite-svelte';

    export let href: string | undefined = undefined;
</script>

<DropdownItem {href} class="hover:bg-primary-700" on:click>
    <slot/>
</DropdownItem>

