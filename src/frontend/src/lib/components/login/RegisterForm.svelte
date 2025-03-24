<script lang="ts">
    import LL from "$i18n/i18n-svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    export let email = "";
    export let password = "";
    export let old_password = "";
    export let is_change = false;
    export let is_reset = false;

    const min_length = 14;

    let confirm_password = "";

    $: button_disabled = password.length < 14 || password != confirm_password;
</script>

<div class="form">
    <form on:submit|preventDefault>
        {#if !is_change}
            <div class="option">
                <span class="item-label">
                    <label for="email">{$LL.LOGIN.EMAIL()}</label>
                </span>
                <input name="email" type="email" bind:value={email} disabled={is_reset} required/>
            </div>
        {/if}
        {#if is_change}
            <div class="option">
                <span class="item-label">
                    <label for="old-password">
                        {$LL.LOGIN.OLD_PASSWORD()}
                    </label>
                </span>
                <input name="old-password" type="password" bind:value={old_password}/>
            </div>
        {/if}
        <div class="option">
            <span class="item-label">
                <label for="password">
                    {#if is_reset}
                        {$LL.LOGIN.NEW_PASSWORD()}
                    {:else}
                        {$LL.LOGIN.PASSWORD()}
                    {/if}
                </label>
            </span>
            <input name="password" type="password" minlength={min_length} maxlength=64 bind:value={password} required/>
        </div>
        <div class="option">
            <span class="item-label">
                <label for="confirm-password">{$LL.LOGIN.CONFIRM_PASSWORD()}</label>
            </span>
            <input name="confirm-password" type="password" minlength={min_length} maxlength=64 bind:value={confirm_password} required/>
        </div>
        <div class="errors option">
            {#if password.length && password.length < min_length}
                <div>
                    {$LL.LOGIN.PASSWORD_CHARACTER_WARNING({count: min_length})}
                </div>
            {/if}
            {#if password !== confirm_password}
                <div>
                    {$LL.LOGIN.PASSWORD_NO_MATCH()}
                </div>
            {/if}
        </div>
        <div>
            <Button type="submit" disabled={button_disabled}>
                {#if is_change}
                    {$LL.LOGIN.CHANGE_PASSWORD()}
                {:else if is_reset}
                    {$LL.LOGIN.RESET_PASSWORD()}
                {:else}
                    {$LL.LOGIN.REGISTER()}
                {/if}
            </Button>
        </div>
    </form>
</div>



<style>
    .form {
        min-width: 400px;
    }
    span.item-label {
        display: inline-block;
        width: 150px;
    }
    .option {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .errors {
        color: #FFCCCB;
    }
</style>