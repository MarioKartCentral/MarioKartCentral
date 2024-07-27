<script lang="ts">
    import { onMount } from 'svelte';
    import type { PlayerInfo } from '$lib/types/player-info';
    import LL from "$i18n/i18n-svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { findNumberOfDaysBetweenDates, default_player_ban_options } from '$lib/util/util'

    export let player: PlayerInfo;
    export let isEditBan: boolean = false;
    export let handleCancel: () => void | null = null

    let isIndefinite: boolean | null = true;
    let numDays: number | null = null;
    let reason: string | null = null;
    let customReason: string | null = null;

    onMount(async () => {
        if (!player.ban_info) {
            const res = await fetch(`/api/registry/players/${player.id}`)
            if (res.status === 200) {
                player = await res.json()
            }
        }
        if (player.ban_info) {
            isIndefinite = player.ban_info.is_indefinite
            numDays = isIndefinite ? null : findNumberOfDaysBetweenDates(player.ban_info.ban_date, player.ban_info.expiration_date)
            reason = player.ban_info.reason
            if (!default_player_ban_options.includes(player.ban_info.reason)) {
                reason = 'Other'
                customReason = player.ban_info.reason
            }
        }
    });

    async function banPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if (!player)
            return alert('A player is not selected')
    
        let confirmText = `Are you sure you want to ban ${player.name}?`
        if (isEditBan)
            confirmText = `Are you sure you want to edit the ban for ${player.name}?`
        const confirm = window.confirm(confirmText)
        if (!confirm)
            return
        
        const data = new FormData(event.currentTarget)
        let expirationDate = 0
        let days = Number(data.get('days'))
        if (days) {
            const startDate = player.ban_info?.ban_date || Math.floor(Date.now()/1000)
            expirationDate = startDate + 86400*days
        }

        const payload = {
            is_indefinite: data.get('duration') === 'indefinite',
            expiration_date: expirationDate,
            reason: data.get('custom_reason') || data.get('reason')
        };

        const endpoint = isEditBan ? `/api/registry/players/${player.id}/editBan` : `/api/registry/players/${player.id}/ban`
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json()

        if (response.status < 300) {
            if (isEditBan)
                alert(`Successfully edited the ban for ${player.name} (Player ID: ${player.id})`)
            else
                alert(`Successfully banned ${player.name} (Player ID: ${player.id})`)
            window.location.reload()
        } else {
            const detail = result.detail ? `, ${result.detail}` : ''
            alert(`${result.title}${detail}`)
        }
    }

    function handleDurationChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
        isIndefinite = event.currentTarget.value === 'indefinite'
    }
</script>

<div>
    <h2> {#if isEditBan} {$LL.PLAYER_BAN.EDIT_BAN_DETAILS()} {:else} {$LL.PLAYER_BAN.BAN_DETAILS()} {/if}</h2>
    <form method="post" on:submit|preventDefault={banPlayer}>
        <div>
            <label for="duration">{$LL.PLAYER_BAN.DURATION()} {#if isEditBan}({$LL.PLAYER_BAN.FROM_INITIAL_BAN_DATE()}){/if}</label> <br/>
            <select name="duration" value={isIndefinite ? 'indefinite' : 'number of days'} on:change={handleDurationChange} required>
                <option value='indefinite'>{$LL.PLAYER_BAN.INDEFINITE()}</option>
                <option value='number of days'>{$LL.PLAYER_BAN.NUMBER_OF_DAYS()}</option>
            </select>
            {#if !isIndefinite}
                <input name='days' type='number' min='1' step='1' value={numDays} required/>
            {/if}
        </div>
        <div>
            <label for="reason">{$LL.PLAYER_BAN.REASON()}</label> <br/>
            <select name='reason' bind:value={reason} required>
                <option value={null} disabled>{$LL.PLAYER_BAN.SELECT_REASON()}</option>
                {#each default_player_ban_options as o}
                    <option value={o}>{o}</option>
                {/each}
            </select>
            {#if reason === 'Other'}
                <input name='custom_reason' type='text' placeholder={$LL.PLAYER_BAN.ENTER_REASON()} value={customReason} required/>
            {/if}
        </div>
        <br/>
        <Button type="submit">{$LL.PLAYER_BAN.SUBMIT()}</Button>
        {#if handleCancel}
            <Button color='red' on:click={handleCancel}>{$LL.PLAYER_BAN.CANCEL()}</Button>
        {/if}
    </form>
</div>

<style>
    h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    input[name="days"] {
        width: 60px;
    }
    input[name="custom_reason"] {
        width: 300px;
    }
</style>
