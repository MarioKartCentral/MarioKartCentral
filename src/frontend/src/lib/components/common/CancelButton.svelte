<script lang="ts">
    import { Button } from "flowbite-svelte";
    import { CloseSolid } from "flowbite-svelte-icons";
</script>

<Button pill={true} class="!p-2" on:click>
    <CloseSolid class="w-4 h-4"/>
</Button>