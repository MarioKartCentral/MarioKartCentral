<script lang="ts">
    import { Button } from "flowbite-svelte";

    export let href: string | undefined = undefined;
    export let circle = false;
    export let type: "submit" | "button" | "reset" | null | undefined = "button";
    export let size: "xs" | "sm" | "lg" | "xl" | "md" = "sm";
    export let disabled = false;
</script>

<Button {size} pill={circle} class="{circle ? '!p-2' : ''}" {href} on:click {type} {disabled}>
    <slot/>
</Button>