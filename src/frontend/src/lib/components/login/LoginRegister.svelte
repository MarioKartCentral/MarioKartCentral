<script lang="ts">
    import LL from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import type { UserAccountInfo } from '$lib/types/user-account-info';
    import Tabs from '$lib/components/common/tabs/Tabs.svelte';
    import TabItem from '$lib/components/common/tabs/TabItem.svelte';
    import RegisterForm from './RegisterForm.svelte';

    export let send_to: string | null = null;

    let working = false; // used to prevent double clicking

    let email = "";
    let password = "";

    async function loginOrSignup(isLogin: boolean) {
        working = true;
        const { getFingerprint, getFingerprintData } = await import('@thumbmarkjs/thumbmarkjs');
        const fingerprint = await getFingerprint();
        const fingerprintData = await getFingerprintData();
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const payload = { 
            email: email, 
            password: password,
            fingerprint: {hash: fingerprint, data: fingerprintData},
        };

        const endpoint = isLogin ? '/api/user/login' : '/api/user/signup';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        working = false;
        const result = await response.json();
        if (response.status < 300) {
            const user: UserAccountInfo = result;
            if(user.force_password_reset) {
                alert($LL.LOGIN.PASSWORD_RESET_REQUIRED());
                return;
            }
            if(!isLogin) {
                // don't use goto since we want to refresh the page state with logged in status
                window.location.href = `/${$page.params.lang}/user/confirm-email`;
            }
            else if(send_to !== null) {
                window.location.href = send_to;
            }
            else {
                window.location.reload();
            }
        } else {
            if(isLogin) {
                alert(`${$LL.LOGIN.LOGIN_FAILED()}: ${result['title']}`)
            }
            else {
                alert(`${$LL.LOGIN.REGISTRATION_FAILED()}: ${result['title']}`)
            }
        }
    }
</script>

<Tabs>
    <TabItem open title={$LL.LOGIN.TRANSFER()}>
        <div class="form">
            <div class="option">
                {$LL.LOGIN.TRANSFER_ACCOUNT_PROMPT()}
            </div>
            <div>
                <Button href="/{$page.params.lang}/user/transfer-account">{$LL.LOGIN.TRANSFER_ACCOUNT()}</Button>
            </div>
        </div>
    </TabItem>
    <TabItem title={$LL.LOGIN.LOGIN()}>
        <div class="form">
            <form method="post" on:submit|preventDefault={() => loginOrSignup(true)}>
                <div class="option">
                    <span class="item-label">
                        <label for="email">{$LL.LOGIN.EMAIL()}</label>
                    </span>
                    <input name="email" type="email" required bind:value={email}/>
                </div>
                <div class="option">
                    <span class="item-label">
                        <label for="password">{$LL.LOGIN.PASSWORD()}</label>
                    </span>
                    <input name="password" type="password" required bind:value={password}/>
                </div>
                <div class="login-row">
                    <Button extra_classes="login-btn" type="submit" disabled={working}>{$LL.LOGIN.LOGIN()}</Button>
                    <div>
                        <a href="/{$page.params.lang}/user/reset-password">
                            {$LL.LOGIN.FORGOT_PASSWORD()}
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </TabItem>
    <TabItem title={$LL.LOGIN.REGISTER()}>
        <RegisterForm bind:email={email} bind:password={password} on:submit={() => loginOrSignup(false)}/>
    </TabItem>
</Tabs>

<style>
    div.form {
        width: 300px;
    }
    div.option {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    div.login-row {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    span.item-label {
        display: inline-block;
        width: 150px;
    }
</style>