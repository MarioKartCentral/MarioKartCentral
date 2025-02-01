<script lang="ts">
    import type { Discord } from "$lib/types/discord";
    import DiscordName from "./DiscordName.svelte";
    import DiscordUser from "./DiscordUser.svelte";
    import { Popover } from "flowbite-svelte";

    export let discord: Discord | null;
</script>

{#if discord}
    <div id="name">
        <DiscordName {discord}/>
    </div>
    <Popover class="bg-gray-600 text-white">
        <DiscordUser {discord}/>
    </Popover>
{/if}
