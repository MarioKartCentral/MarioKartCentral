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

<form on:submit|preventDefault>
    {#if !is_change}
        <div class="option">
            <label for="email">{$LL.LOGIN.EMAIL()}</label>
            <input name="email" type="email" bind:value={email} disabled={is_reset} required/>
        </div>
    {/if}
    {#if is_change}
        <div class="option">
            <label for="old-password">
                Old Password
            </label>
            <input name="old-password" type="password" bind:value={old_password}/>
        </div>
    {/if}
    <div class="option">
        <label for="password">
            {#if is_reset}
                New Password
            {:else}
                {$LL.LOGIN.PASSWORD()}
            {/if}
        </label>
        <input name="password" type="password" minlength={min_length} maxlength=64 bind:value={password} required/>
    </div>
    <div class="option">
        <label for="confirm-password">Confirm Password</label>
        <input name="confirm-password" type="password" minlength={min_length} maxlength=64 bind:value={confirm_password} required/>
    </div>
    <div class="errors option">
        {#if password.length && password.length < min_length}
            <div>
                Password must be at least {min_length} characters!
            </div>
        {/if}
        {#if password !== confirm_password}
            <div>
                Passwords do not match!
            </div>
        {/if}
    </div>
    <div>
        <Button type="submit" disabled={button_disabled}>
            {#if is_change}
                Change Password
            {:else if is_reset}
                Reset Password
            {:else}
                Register
            {/if}
        </Button>
    </div>
</form>


<style>
    label {
        display: inline-block;
        min-width: 150px;
    }
    .option {
        margin-bottom: 10px;
    }
    .errors {
        color: #FFCCCB;
    }
</style>