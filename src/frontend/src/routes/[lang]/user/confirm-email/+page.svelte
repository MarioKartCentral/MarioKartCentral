<script lang="ts">
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";

    let disable_button = false;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    onMount(async() => {
        let token = $page.url.searchParams.get('token');
        if(token === null) {
            return;
        }
        const payload = {
            token_id: token,
        };
        const endpoint = `/api/user/confirm_email`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.EMAIL_CONFIRMATION_SUCCESS());
            if(user_info.player_id) {
                window.location.href = `/${$page.params.lang}/`;
            }
            else {
                window.location.href = `/${$page.params.lang}/user/player-signup`;
            }
        }
        else {
            alert(`${$LL.LOGIN.EMAIL_CONFIRMATION_FAILURE()}: ${result['title']}`);
        }
    });

    async function send_confirmation_email() {
        disable_button = true;
        const endpoint = `/api/user/send_confirmation_email`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.SEND_CONFIRMATION_EMAIL_SUCCESS());
        }
        else {
            alert(`${$LL.LOGIN.SEND_CONFIRMATION_EMAIL_FAILURE()}: ${result['title']}`);
        }
    }
</script>

<Section header={$LL.LOGIN.CONFIRM_EMAIL()}>
    {#if user_info.is_checked}
        {#if user_info.id === null}
            <div>
                {$LL.COMMON.LOGIN_REQUIRED()}
            </div>
        {:else if user_info.email_confirmed}
            <div>
                {$LL.LOGIN.EMAIL_ALREADY_CONFIRMED()}
            </div>
        {:else}
            <div class="welcome section">
                {$LL.LOGIN.WELCOME_TO_MKC()}
            </div>
            <div class="section">
                {$LL.LOGIN.EMAIL_CONFIRMATION_REQUIRED()}
            </div>
            <div class="section">
                <Button disabled={disable_button} on:click={send_confirmation_email}>{$LL.LOGIN.SEND_CONFIRMATION_EMAIL()}</Button>
            </div>
        {/if}
    {/if}
</Section>

<style>
    .welcome {
        font-size: larger;
    }
    .section {
        margin-bottom: 10px;
    }
</style>