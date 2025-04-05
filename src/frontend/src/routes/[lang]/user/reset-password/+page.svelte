<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { User } from "$lib/types/user";
    import RegisterForm from "$lib/components/login/RegisterForm.svelte";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import LL from "$i18n/i18n-svelte";

    let working = true;
    let token_expired = false;
    let token: string | null = null;
    let user_data: User | null = null;
    let new_password: string = "";
    let email_sent = false;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        token = $page.url.searchParams.get('token');
        if(token === null) {
            working = false;
            return;
        }
        const payload = {
            token_id: token,
        };
        const endpoint = '/api/user/check_password_token';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            user_data = result;
            working = false;
            return;
        }
        else {
            token_expired = true;
            working = false;
            return;
        }
    });

    async function reset_password() {
        const payload = {
            token_id: token,
            new_password: new_password,
        };
        const endpoint = '/api/user/reset_password_token';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.PASSWORD_RESET_SUCCESS());
            window.location.href = `/${$page.params.lang}/`;
        }
        else {
            alert(`${$LL.LOGIN.PASSWORD_RESET_FAILURE()}: ${result['title']}`);
        }
    }

    async function send_reset_email(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            email: data.get('email')?.toString(),
        };
        const endpoint = '/api/user/forgot_password';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.SEND_PASSWORD_RESET_EMAIL_SUCCESS());
            email_sent = true;
        }
        else {
            alert(`${$LL.LOGIN.SEND_PASSWORD_RESET_EMAIL_FAILURE()}: ${result['title']}`);
        }
    }
</script>

<svelte:head>
    <title>Reset Password | MKCentral</title>
</svelte:head>

<Section header={$LL.LOGIN.RESET_PASSWORD()}>
    {#if user_info.id !== null}
        {$LL.COMMON.LOGOUT_REQUIRED()}
    {:else if !working}
        {#if token_expired || token === null}
            {#if token_expired}
                <div class="option">
                    {$LL.LOGIN.PASSWORD_RESET_TOKEN_EXPIRED()}
                </div>
            {/if}
            <div>
                <form on:submit|preventDefault={send_reset_email}>
                    <div class="option">
                        <label for="email">
                            {$LL.LOGIN.EMAIL_ADDRESS()}
                        </label>
                        <input type="email" name="email"/>
                    </div>
                    <div>
                        <Button type="submit" disabled={email_sent}>{$LL.LOGIN.SEND_PASSWORD_RESET_EMAIL()}</Button>
                    </div>
                </form>
            </div>
        {:else if user_data}
            <div>
                <RegisterForm email={user_data.email} bind:password={new_password} is_reset on:submit={reset_password}/>
            </div>
        {/if}
    {/if}
</Section>

<style>
    label {
        display: inline-block;
        min-width: 150px;
    }
    .option {
        margin-bottom: 10px;
    }
</style>