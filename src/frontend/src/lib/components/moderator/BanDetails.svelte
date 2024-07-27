<script lang="ts">
    import { onMount } from 'svelte';
    import LL from "$i18n/i18n-svelte";
    import { page } from '$app/stores';
    import type { PlayerInfo } from '$lib/types/player-info';
    import { findNumberOfDaysBetweenDates } from '$lib/util/util'

    export let player: PlayerInfo;
    
    let bannedBy: PlayerInfo | null = null;
    let daysRemaining: string = ''
    let duration: number = 0;

    onMount(async () => {
        if (!player.ban_info)
            return
        
        const nowSeconds: number = Math.floor(Date.now() / 1000)
        const days: number = findNumberOfDaysBetweenDates(nowSeconds, player.ban_info.expiration_date)
        if (days >= 0)
            daysRemaining = days === 1 ? `(${$LL.PLAYER_BAN.IN_DDD_DAY()?.replace('ddd', days)})` : `(${$LL.PLAYER_BAN.IN_DDD_DAYS()?.replace('ddd', days)})`
        duration = findNumberOfDaysBetweenDates(player.ban_info.ban_date, player.ban_info.expiration_date)
        
        const res = await fetch(`/api/registry/players/${player.ban_info.banned_by}`)
        if (res.status === 200)
            bannedBy = await res.json()
    });

    function unixTimestampToString(timestamp: number) {
        let date = new Date(timestamp * 1000)
        return date.toLocaleString($page.params.lang)
    }
</script>

{#if player.ban_info}
    <h2>{$LL.PLAYER_BAN.BAN_DETAILS()}</h2>
    <p>
    <strong>{$LL.PLAYER_BAN.PLAYER()}</strong>: <a href={`/registry/players/profile?id=${player.id}`}>{player.name}</a> <br/>
    <strong>{$LL.PLAYER_BAN.BANNED_BY()}</strong>: {#if bannedBy} <a href={`/registry/players/profile?id=${bannedBy.id}`}>{bannedBy.name}</a> {:else} {$LL.PLAYER_BAN.STAFF()} {/if} <br/>
    <strong>{$LL.PLAYER_BAN.IS_INDEFINITE()}</strong>: {player.ban_info.is_indefinite ? $LL.PLAYER_BAN.YES() : $LL.PLAYER_BAN.NO()} <br/>
    <strong>{$LL.PLAYER_BAN.BANNED()}</strong>: {unixTimestampToString(player.ban_info.ban_date)} <br/>
    {#if !player.ban_info.is_indefinite}
        <strong>{$LL.PLAYER_BAN.UNBANNED()}</strong>: {unixTimestampToString(player.ban_info.expiration_date)} {daysRemaining}<br/>
        <strong>{$LL.PLAYER_BAN.DURATION()}</strong>: {duration} {duration > 1 ? $LL.PLAYER_BAN.DAYS() : $LL.PLAYER_BAN.DAYS()}<br/>
    {/if}
    <strong>{$LL.PLAYER_BAN.REASON()}</strong>: {player.ban_info.reason}
    </p>
{/if}

<style>
    h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 5px;
    }
</style>

