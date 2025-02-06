<script lang="ts">
    import type { FriendCode } from "$lib/types/friend-code";
    import { Popover } from "flowbite-svelte";
    import FCTypeBadge from "../badges/FCTypeBadge.svelte";
    import { fc_type_order } from "$lib/util/util";
    import LL from "$i18n/i18n-svelte";

    export let friend_codes: FriendCode[];
    export let selected_fc_id: number | null = null;

    // we want to display the selected FC if there is one, otherwise just display the first FC in the list
    function get_display_fc() {
        let fc = friend_codes.find((fc) => fc.id === selected_fc_id);
        if(!fc) {
            let filtered_fcs = friend_codes.filter((fc) => fc.is_active);
            if(!filtered_fcs.length) return null;
            fc = filtered_fcs[0];
        }
        return fc;
    }

    let display_fc = get_display_fc();

    function get_other_fcs() {
        if(!selected_fc_id) {
            return friend_codes.filter((fc) => fc.is_active).toSorted((a, b) => fc_type_order[a.type] - fc_type_order[b.type]);
        }
        return friend_codes.filter((fc) => fc !== display_fc && fc.is_active).toSorted((a, b) => fc_type_order[a.type] - fc_type_order[b.type]);
    }

    let other_fcs = get_other_fcs();
</script>

{#if display_fc}
    <div class="default_view" id="fc">
        {display_fc.fc}   
    </div>
    <Popover class="bg-gray-600 text-white">
        {#if selected_fc_id}
            <div class="selected">{$LL.FRIEND_CODES.SELECTED_FC()}</div>
            <div>
                <FCTypeBadge type={display_fc.type}/>
                {display_fc.fc}
            </div>
        {/if}
        {#if selected_fc_id && other_fcs.length}
            <div class="selected">{$LL.FRIEND_CODES.OTHER_FCS()}</div>
        {/if}
        {#each other_fcs as fc}
            <div>
                <FCTypeBadge type={fc.type}/>
                {fc.fc}
            </div> 
        {/each}
    </Popover>
{/if}


<style>
    div.default_view {
        width: fit-content;
    }
    div.selected {
        font-weight: bold;
    }
</style>