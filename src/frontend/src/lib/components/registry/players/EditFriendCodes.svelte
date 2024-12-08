<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import GameBadge from "$lib/components/badges/GameBadge.svelte";
    import Dialog from '$lib/components/common/Dialog.svelte';
    import Button from "$lib/components/common/buttons/Button.svelte";
    import FriendCodeForm from "./FriendCodeForm.svelte";
    import LL from "$i18n/i18n-svelte";
    import { EditSolid } from "flowbite-svelte-icons";
    import type { FriendCode } from "$lib/types/friend-code";

    export let player: PlayerInfo;
    export let is_privileged = false;

    let add_fc_dialog: Dialog;
    let edit_fc_dialog: Dialog;
    let selected_fc: FriendCode;

    let friend_codes = is_privileged ? player.friend_codes : player.friend_codes.filter((f) => f.is_active);

    function open_edit_dialog(fc: FriendCode) {
        selected_fc = fc;
        edit_fc_dialog.open();
        console.log(is_privileged);
    }

    async function edit_fc_privileged(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        console.log(data.get('is_primary'));
        const payload = {
            player_id: player.id,
            id: selected_fc?.id,
            fc: data.get('fc')?.toString().replaceAll(" ", "-"),
            is_primary: data.get('is_primary') ? true : false,
            description: data.get('description')?.toString(),
            is_active: data.get('is_active') ? true : false,
        };
        console.log(payload);
        const endpoint = '/api/registry/forceEditFriendCode';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.FRIEND_CODES.FRIEND_CODE_EDIT_FAILED()}: ${result['title']}`);
        }
    }

    async function edit_fc(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            id: selected_fc?.id,
            is_primary: data.get('is_primary') ? true : false,
            description: data.get('description')?.toString(),
        };
        console.log(payload);
        const endpoint = '/api/registry/editFriendCode';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.FRIEND_CODES.FRIEND_CODE_EDIT_FAILED()}: ${result['title']}`);
        }
    }
</script>

{#each friend_codes as fc}
    <div class="flex">
        <GameBadge game={fc.game}/>
        {fc.fc}
        {#if !fc.is_active}
            ({$LL.FRIEND_CODES.INACTIVE()})
        {/if}
        <EditSolid on:click={() => open_edit_dialog(fc)}/>
    </div>
{/each}
<div class="button">
    <Button on:click={add_fc_dialog.open}>{$LL.FRIEND_CODES.ADD_FRIEND_CODE()}</Button>
</div>

<Dialog bind:this={add_fc_dialog} header={$LL.FRIEND_CODES.ADD_FRIEND_CODE()}>
    <FriendCodeForm {player} {is_privileged}/>
</Dialog>

<Dialog bind:this={edit_fc_dialog} header={$LL.FRIEND_CODES.EDIT_FRIEND_CODE()}>
    {#if selected_fc}
        <form method="post" on:submit|preventDefault={is_privileged ? edit_fc_privileged : edit_fc}>
            <div>
                <div class="option">
                    <div>
                        <label for="fc">{$LL.FRIEND_CODES.FRIEND_CODE()}</label>
                    </div>
                    <div>
                        <input name="fc" placeholder={selected_fc.game !== 'mk8' ? '0000-0000-0000' : 'NNID'} 
                        minlength={selected_fc.game === 'mk8' ? 6 : null} maxlength={selected_fc.game === 'mk8' ? 16 : null} 
                        disabled={!is_privileged} value={selected_fc.fc} required/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="is_primary">{$LL.FRIEND_CODES.PRIMARY()}</label>
                    </div>
                    <div>
                        <input name="is_primary" type="checkbox" checked={selected_fc.is_primary}/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="description">{$LL.FRIEND_CODES.DESCRIPTION()}</label>
                    </div>
                    <div>
                        <input name="description" placeholder={$LL.FRIEND_CODES.DESCRIPTION()} value={selected_fc.description}/>
                    </div>
                </div>
                {#if is_privileged}
                    <div class="option">
                        <div>
                            <label for="is_active">{$LL.FRIEND_CODES.ACTIVE()}</label>
                        </div>
                        <div>
                            <input name="is_active" type="checkbox" checked={selected_fc.is_active}/>
                        </div>
                    </div>
                {/if}
                <Button type="submit">{$LL.EDIT()}</Button>
            </div>
        </form>
    {/if}
</Dialog>

<style>
    div.button {
      margin-top: 20px;
    }
    div.flex {
        display: flex;
        gap: 5px;
    }
    .option {
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
  </style>