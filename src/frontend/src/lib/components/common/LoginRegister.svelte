<script lang="ts">
    import LL from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
    import Button from './buttons/Button.svelte';
    import type { UserAccountInfo } from '$lib/types/user-account-info';

    export let send_to: string | null = null;

    let working = false; // used to prevent double clicking

    async function loginOrSignup(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        working = true;
        const data = new FormData(event.currentTarget);
        const { getFingerprint, getFingerprintData } = await import('@thumbmarkjs/thumbmarkjs');
        const fingerprint = await getFingerprint();
        const fingerprintData = await getFingerprintData();
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const payload = { 
            email: data.get('email')!.toString(), 
            password: data.get('password')!.toString(),
            fingerprint: {hash: fingerprint, data: fingerprintData},
        };

        const isLogin = event.submitter?.classList.contains('login-btn') ?? false;
        const endpoint = isLogin ? '/api/user/login' : '/api/user/signup';
        console.log({ data, isLogin, endpoint });
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        working = false;
        if (response.status < 300) {
            const user: UserAccountInfo = await response.json();
            if(user.force_password_reset) {
                alert("You must reset your password before logging in. Check your email for a password reset link.");
                return;
            }
            if(!isLogin) {
                // don't use goto since we want to refresh the page state with logged in status
                window.location.href = `/${$page.params.lang}/user/player-signup`;
            }
            else if(send_to !== null) {
                window.location.href = send_to;
            }
            else {
                window.location.reload();
            }
        } else {
            if(isLogin) {
                alert($LL.LOGIN.LOGIN_FAILED())
            }
            else {
                alert($LL.LOGIN.REGISTRATION_FAILED())
            }
        }
    }
</script>

<div class="form">
    <form method="post" on:submit|preventDefault={loginOrSignup}>
        <div class="field">
            <span class="item-label">
                <label for="email">{$LL.LOGIN.EMAIL()}</label>
            </span>
            <input name="email" type="email" required/>
        </div>
        <div class="field">
            <span class="item-label">
                <label for="password">{$LL.LOGIN.PASSWORD()}</label>
            </span>
            <input name="password" type="password" required/>
        </div>
        <Button extra_classes="login-btn" type="submit" disabled={working}>{$LL.NAVBAR.LOGIN()}</Button>
        <Button extra_classes="register-btn" type="submit" disabled={working}>{$LL.NAVBAR.REGISTER()}</Button>
    </form>
</div>


<style>
    div.form {
        padding: 10px;
    }
    div.field {
        margin-bottom: 5px;
    }
    span.item-label {
        display: inline-block;
        width: 100px;
    }
</style>