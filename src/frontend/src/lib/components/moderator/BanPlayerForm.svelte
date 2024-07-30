<script lang="ts">
    import { onMount } from 'svelte';
    import type { PlayerInfo } from '$lib/types/player-info';
    import type { BanInfoDetailed } from '$lib/types/ban-info';
    import LL from "$i18n/i18n-svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import { findNumberOfDaysBetweenDates, default_player_ban_options } from '$lib/util/util'

    // use playerId and playerName instead of full PlayerInfo object since the /player_bans page doesn't fetch PlayerInfo 
    export let playerId: number;
    export let playerName: string;
    export let banInfo: BanInfoDetailed | null = null;
    export let isEditBan: boolean = false;
    export let handleCancel: (() => void) | null = null

    let isIndefinite: boolean | null = true;
    let numDays: number | null = null;
    let reason: string | null = null;
    let customReason: string | null = null;

    onMount(async () => {
        if (!banInfo) {
            const res = await fetch(`/api/registry/players/${playerId}`)
            if (res.status === 200) {
                const player: PlayerInfo = await res.json()
                banInfo = player.ban_info
            }
        }
        if (banInfo) {
            isIndefinite = banInfo.is_indefinite
            numDays = isIndefinite ? null : findNumberOfDaysBetweenDates(banInfo.ban_date, banInfo.expiration_date)
            reason = banInfo.reason
            if (!default_player_ban_options.includes(banInfo.reason)) {
                reason = 'Other'
                customReason = banInfo.reason
            }
        }
    });

    async function banPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        let confirmText = `Are you sure you want to ban ${playerName}?`
        if (isEditBan)
            confirmText = `Are you sure you want to edit the ban for ${playerName}?`
        const confirm = window.confirm(confirmText)
        if (!confirm)
            return
        
        const data = new FormData(event.currentTarget)
        let expirationDate = 0
        let days = Number(data.get('days'))
        if (days) {
            const startDate = banInfo?.ban_date || Math.floor(Date.now()/1000)
            expirationDate = startDate + 86400*days
        }

        const payload = {
            is_indefinite: data.get('duration') === 'indefinite',
            expiration_date: expirationDate,
            reason: data.get('custom_reason') || data.get('reason')
        };

        const endpoint = isEditBan ? `/api/registry/players/${playerId}/editBan` : `/api/registry/players/${playerId}/ban`
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json()

        if (response.status < 300) {
            if (isEditBan)
                alert(`Successfully edited the ban for ${playerName} (Player ID: ${playerId})`)
            else
                alert(`Successfully banned ${playerName} (Player ID: ${playerId})`)
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
    <form on:submit|preventDefault={banPlayer}>
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
