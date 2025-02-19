<script lang="ts">
    import LL from "$i18n/i18n-svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import FCTypeSelect from "$lib/components/common/FCTypeSelect.svelte";

    export let player: PlayerInfo | null;
    export let is_privileged = false;
    let selected_type: string | null = null;

    const fc_limits: { [key: string]: number } = { switch: 1, mkt: 1, mkw: 4, '3ds': 1, nnid: 1 };

    function get_maxed_types() {
        // if we're privileged, we can add fcs for any game
        if(!player || is_privileged) return [];
        // get all games where we have reached the FC limit
        let maxed_types = Object.keys(fc_limits).filter(
            (type) => player.friend_codes.filter((fc) => fc.type === type && fc.is_active).length >= fc_limits[type]
        );
        return maxed_types;
    }

    async function addFC(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            fc: data.get('fc')?.toString().replaceAll(" ", "-"),
            type: data.get('fc_type')?.toString(),
            is_primary: data.get('is_primary') ? true : false,
            description: data.get('description')?.toString(),
        };
        console.log(payload);
        const endpoint = '/api/registry/addFriendCode';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.FRIEND_CODES.FRIEND_CODE_ADD_FAILED()}: ${result['title']}`);
        }
    }

    async function forceAddFC(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            player_id: player?.id,
            fc: data.get('fc')?.toString().replaceAll(" ", "-"),
            type: data.get('fc_type')?.toString(),
            is_primary: data.get('is_primary') ? true : false,
            description: data.get('description')?.toString(),
        };
        console.log(payload);
        const endpoint = '/api/registry/forceAddFriendCode';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.FRIEND_CODES.FRIEND_CODE_ADD_FAILED()}: ${result['title']}`);
        }
    }
</script>

{#if player}
    <form method="post" on:submit|preventDefault={is_privileged ? forceAddFC : addFC}>
        <div>
            <div class="option">
                <FCTypeSelect bind:type={selected_type} flex required disabled_types={get_maxed_types()}/>
            </div>
            <div class="option">
                <div>
                    <label for="fc">{$LL.FRIEND_CODES.FRIEND_CODE()}</label>
                </div>
                <div>
                    <input name="fc" placeholder={selected_type !== 'nnid' ? '0000-0000-0000' : 'NNID'} 
                    minlength={selected_type === 'nnid' ? 6 : null} maxlength={selected_type === 'nnid' ? 16 : null} 
                    required/>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="is_primary">{$LL.FRIEND_CODES.PRIMARY()}</label>
                </div>
                <div>
                    <input name="is_primary" type="checkbox" />
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="description">{$LL.FRIEND_CODES.DESCRIPTION()}</label>
                </div>
                <div>
                    <input name="description" placeholder={$LL.FRIEND_CODES.DESCRIPTION()} />
                </div>
            </div>
            <Button type="submit">{$LL.COMMON.SUBMIT()}</Button>
        </div>
    </form>
{/if}

<style>
    :global(label) {
        display: inline-block;
        width: 100px;
        margin-right: 10px;
    }
    input {
        width: 200px;
    }
    input[type=checkbox] {
        width: 15px;
    }
    .option {
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
</style>