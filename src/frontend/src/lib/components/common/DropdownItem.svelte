<script lang="ts">
    import { DropdownItem } from 'flowbite-svelte';

    export let href: string | undefined = undefined;
</script>

<DropdownItem {href} class="hover:bg-green-600" on:click>
    <slot/>
</DropdownItem>

