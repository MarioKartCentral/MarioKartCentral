<script lang="ts">
    import LL from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
    import Button from './buttons/Button.svelte';

    export let send_to: string | null = null;

    async function loginOrSignup(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
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

        if (response.status < 300) {
            if(!isLogin) {
                // don't use goto since we want to refresh the page state with logged in status
                window.location.href = `/${$page.params.lang}/player-signup`;
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
        <Button extra_classes="login-btn" type="submit">{$LL.NAVBAR.LOGIN()}</Button>
        <Button extra_classes="register-btn" type="submit">{$LL.NAVBAR.REGISTER()}</Button>
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