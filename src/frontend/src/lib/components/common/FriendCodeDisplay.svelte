<script lang="ts">
    import type { FriendCode } from "$lib/types/friend-code";
    import { Popover } from "flowbite-svelte";
    import GameBadge from "../badges/GameBadge.svelte";

    export let friend_codes: FriendCode[];
    export let selected_fc_id: number | null = null;

    // we want to display the selected FC if there is one, otherwise just display the first FC in the list
    function get_display_fc() {
        let fc = friend_codes.find((fc) => fc.id === selected_fc_id);
        if(!fc) {
            fc = friend_codes[0];
        }
        return fc;
    }

    let display_fc = get_display_fc();

    function get_other_fcs() {
        if(!selected_fc_id) {
            return friend_codes;
        }
        return friend_codes.filter((fc) => fc !== display_fc);
    }

    let other_fcs = get_other_fcs();
</script>

<div class="default_view" id="fc">
    {display_fc.fc}   
</div>
<Popover triggeredBy="#fc" class="bg-gray-600 text-white">
    {#if selected_fc_id}
        <div class="selected">Selected FC:</div>
        <div>
            <GameBadge game={display_fc.game}/>
            {display_fc.fc}
        </div>
    {/if}
    {#if selected_fc_id && other_fcs.length}
        <div class="selected">Other FCs:</div>
    {/if}
    {#each other_fcs as fc}
        <div>
            <GameBadge game={fc.game}/>
            {fc.fc}
        </div> 
    {/each}
</Popover>

<style>
    div.default_view {
        width: fit-content;
    }
    div.selected {
        font-weight: bold;
    }
</style>