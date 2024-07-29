<script lang="ts">
    import type { BanFilter, BanHistoricalFilter } from '$lib/types/ban-filter';
    import type { PlayerInfo } from '$lib/types/player-info';
    import LL from "$i18n/i18n-svelte";
    import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';

    export let filter: BanFilter | BanHistoricalFilter;
    export let maxPage: number = 1;
    
    let player: PlayerInfo | null = null;
    let bannedBy: PlayerInfo | null = null;
    let unbannedBy: PlayerInfo | null = null;

    $: filter.player_id = player?.id || null
    $: filter.banned_by = bannedBy?.id || null
    $: {
        if ('unbanned_by' in filter)
            filter.unbanned_by = unbannedBy?.id || null
    }

    function getDate(value: string, isBefore: boolean) {
        if (!value)
            return null

        const date = new Date(`${value} ${isBefore ? '23:59:59' : ''}`)
        return Math.ceil(date.getTime() / 1000) // divide by 1000 since Python uses seconds instead of ms
    }
</script>

<div class='container'>
    <div>
        <label for="player">{'Player'}</label> <br/>
        <PlayerSearch bind:player={player}/>
    </div>
    <div>
        <label for="bannedBy">{'Banned By'}</label> <br/>
        <PlayerSearch bind:player={bannedBy}/>
    </div>
    {#if 'unbanned_by' in filter}
        <div>
            <label for="unbannedBy">{'Unbanned By'}</label> <br/>
            <PlayerSearch bind:player={unbannedBy}/>
        </div>
    {/if}
    <div>
        <label for="isIndefinite">{'Is Indefinite'}</label> <br/>
        <select name="isIndefinite" bind:value={filter.is_indefinite}>
            <option value={null}></option>
            <option value={true}>{$LL.PLAYER_BAN.YES()}</option>
            <option value={false}>{$LL.PLAYER_BAN.NO()}</option>
        </select>
    </div>
    <div>
        <label for="bannedBefore">{'Banned Before'}</label> <br/>
        <input name='bannedBefore' type='date' on:change={event => {filter.banned_before = getDate(event.currentTarget.value, true)}}/>
    </div>
    <div>
        <label for="bannedAfter">{'Banned After'}</label> <br/>
        <input name='bannedAfter' type='date' on:change={event => {filter.banned_after = getDate(event.currentTarget.value, false)}}/>
    </div>
    <div>
        <label for="expiresBefore">{'Expires Before'}</label> <br/>
        <input name='expiresBefore' type='date' on:change={event => {filter.expires_before = getDate(event.currentTarget.value, true)}}/>
    </div>
    <div>
        <label for="expiresAfter">{'Expires After'}</label> <br/>
        <input name='expiresAfter' type='date' on:change={event => {filter.expires_after = getDate(event.currentTarget.value, false)}}/>
    </div>
    {#if 'unbanned_by' in filter}
        <div>
            <label for="unbannedBefore">{'Unbanned Before'}</label> <br/>
            <input name='unbannedBefore' type='date' on:change={event => {filter.unbanned_before = getDate(event.currentTarget.value, true)}}/>
        </div>
        <div>
            <label for="unbannedAfter">{'Unbanned After'}</label> <br/>
            <input name='unbannedAfter' type='date' on:change={event => {filter.unbanned_before = getDate(event.currentTarget.value, false)}}/>
        </div>
    {/if}
    <div>
        <label for="reason">{'Reason'}</label> <br/>
        <input name='reason' type='text' bind:value={filter.reason} placeholder={$LL.PLAYER_BAN.REASON()}/>
    </div>
    <div>
        <label for="page">{'Page'}</label> <br/>
        <input name='page' type='number' min='1' max={maxPage} step='1' bind:value={filter.page}/>
    </div>
</div>

<style>
    .container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    input[name="page"] {
        width: 60px;
    }
</style>