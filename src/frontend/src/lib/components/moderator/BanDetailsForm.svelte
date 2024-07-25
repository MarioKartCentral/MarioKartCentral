<script lang="ts">
    import LL from "$i18n/i18n-svelte";
    import { default_player_ban_options } from "$lib/util/util";
    import Button from "$lib/components/common/buttons/Button.svelte";

    export let handleSubmit: (event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) => void;
    export let isIndefinite: boolean | null = true;
    export let numDays: number | null = null;
    export let reason: typeof default_player_ban_options[number] | null = null;
    export let customReason: string | null = null;
    
    function handleDurationChange(event: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
        isIndefinite = event.currentTarget.value === 'indefinite'
    }
</script>

<div>
    <h2>Ban Details</h2>
    <form method="post" on:submit|preventDefault={handleSubmit}>
        <div>
            <label for="duration">{$LL.PLAYER_BAN.DURATION()}</label> <br/>
            <select name="duration" on:change={handleDurationChange} required>
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
                <input name='custom_reason' type='text' placeholder='Enter reason' value={customReason} required/>
            {/if}
        </div>
        <br/>
        <Button type="submit">{$LL.PLAYER_BAN.SUBMIT()}</Button>
    </form>
</div>

<style>
    h2 {
        font-size: 20px;
        margin-bottom: 5px;
    }
    input[name="days"] {
        width: 60px;
    }
    input[name="custom_reason"] {
        width: 300px;
    }
</style>