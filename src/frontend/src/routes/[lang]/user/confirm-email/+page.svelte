<script lang="ts">
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Section from "$lib/components/common/Section.svelte";
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';

    let disable_button = false;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
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
            alert("Successfully sent confirmation email!");
        }
        else {
            alert(`Failed to send confirmation email: ${result['title']}`);
        }
    }
</script>

<Section header="Confirm Email">
    {#if user_info.is_checked}
        {#if user_info.id === null}
            <div>
                You are not logged in.
            </div>
        {:else if user_info.email_confirmed}
            <div>
                Your email is already confirmed.
            </div>
        {:else}
            <div class="welcome section">
                Welcome to Mario Kart Central!
            </div>
            <div class="section">
                Before you can complete your player registration, you'll need to verify your email address. You should have received an email containing a link to confirm your email address; if you don't see the email, 
                or the link has expired, you can click the button below to send another confirmation email.
            </div>
            <div class="section">
                <Button disabled={disable_button} on:click={send_confirmation_email}>Send confirmation email</Button>
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