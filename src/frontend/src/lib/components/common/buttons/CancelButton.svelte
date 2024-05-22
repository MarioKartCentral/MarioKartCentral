<script lang="ts">
    import Button from "./Button.svelte";
    import { CloseSolid } from "flowbite-svelte-icons";
</script>

<Button circle={true} on:click>
    <CloseSolid class="w-4 h-4"/>
</Button>