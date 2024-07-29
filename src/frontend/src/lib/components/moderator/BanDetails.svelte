<script lang="ts">
    import { onMount } from 'svelte';
    import LL from "$i18n/i18n-svelte";
    import { page } from '$app/stores';
    import type { BanInfoDetailed } from '$lib/types/ban-info';
    import { findNumberOfDaysBetweenDates } from '$lib/util/util'

    export let banInfo: BanInfoDetailed;
    
    let daysRemaining: string = ''
    let duration: number = 0;

    onMount(async () => {
        const nowSeconds: number = Math.floor(Date.now() / 1000)
        const days: number = Math.max(-1, findNumberOfDaysBetweenDates(nowSeconds, banInfo.expiration_date))
        if (days >= 0)
            daysRemaining = days === 1 ? `(${$LL.PLAYER_BAN.IN_DDD_DAY()?.replace('ddd', days.toString())})` : `(${$LL.PLAYER_BAN.IN_DDD_DAYS()?.replace('ddd', days.toString())})`
        duration = findNumberOfDaysBetweenDates(banInfo.ban_date, banInfo.expiration_date)
    });

    function unixTimestampToString(timestamp: number) {
        let date = new Date(timestamp * 1000)
        return date.toLocaleString($page.params.lang)
    }
</script>

<div>
    <h2>{$LL.PLAYER_BAN.BAN_DETAILS()}</h2>
    <p>
    <strong>{$LL.PLAYER_BAN.PLAYER()}</strong>: <a href={`/registry/players/profile?id=${banInfo.player_id}`}>{banInfo.player_name}</a> <br/>
    <strong>{$LL.PLAYER_BAN.BANNED_BY()}</strong>: {#if banInfo.banned_by_pid} <a href={`/registry/players/profile?id=${banInfo.banned_by_pid}`}>{banInfo.banned_by_name}</a> {:else} {$LL.PLAYER_BAN.USER()} {banInfo.banned_by_uid} {/if} <br/>
    <strong>{$LL.PLAYER_BAN.IS_INDEFINITE()}</strong>: {banInfo.is_indefinite ? $LL.PLAYER_BAN.YES() : $LL.PLAYER_BAN.NO()} <br/>
    <strong>{$LL.PLAYER_BAN.BANNED()}</strong>: {unixTimestampToString(banInfo.ban_date)} <br/>
    {#if !banInfo.is_indefinite }
        <strong>{$LL.PLAYER_BAN.EXPIRES()}</strong>: {unixTimestampToString(banInfo.expiration_date)} {daysRemaining}<br/>
    {/if}
    {#if banInfo.unban_date}
        <strong>{$LL.PLAYER_BAN.UNBANNED()}</strong>: {unixTimestampToString(banInfo.unban_date)}<br/>
        <strong>{$LL.PLAYER_BAN.UNBANNED_BY()}</strong>: {#if banInfo.unbanned_by_pid} <a href={`/registry/players/profile?id=${banInfo.unbanned_by_pid}`}>{banInfo.unbanned_by_name}</a> {:else if banInfo.unbanned_by_uid !== null} {$LL.PLAYER_BAN.USER()} {banInfo.unbanned_by_uid} {:else} {$LL.PLAYER_BAN.SYSTEM()} {/if} <br/>
    {/if}
    {#if !banInfo.is_indefinite }
        <strong>{$LL.PLAYER_BAN.DURATION()}</strong>: {duration} {duration > 1 ? $LL.PLAYER_BAN.DAYS() : $LL.PLAYER_BAN.DAYS()}<br/>
    {/if}
    <strong>{$LL.PLAYER_BAN.REASON()}</strong>: {banInfo.reason}
    </p>
</div>

<style>
    h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 5px;
    }
</style>

