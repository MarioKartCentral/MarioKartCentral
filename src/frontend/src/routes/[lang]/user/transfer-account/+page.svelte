<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import { user } from "$lib/stores/stores";
    import type { UserInfo } from "$lib/types/user-info";
    import LL from "$i18n/i18n-svelte";
    import { page } from "$app/stores";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let player: PlayerInfo | null = null;
    let working = false;
    let agree_terms = false;
    let agree_policy = false;

    async function transfer_account() {
        if(!player) return;
        working = true;
        const payload = {
            player_id: player.id,
        };
        const endpoint = '/api/user/transfer_account';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        working = false;
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.LOGIN.TRANSFER_ACCOUNT_SUCCESS());
            window.location.href = `/${$page.params.lang}/`;
        }
        else {
            alert(`${$LL.LOGIN.TRANSFER_ACCOUNT_FAILED()}: ${result['title']}`);
        }
    }
    
</script>

<svelte:head>
    <title>Transfer Account | MKCentral</title>
</svelte:head>

{#if user_info.is_checked}
    {#if user_info.id === null}
        <Section header={$LL.LOGIN.TRANSFER_ACCOUNT_HEADER()}>
            <div>
                {$LL.LOGIN.TRANSFER_ACCOUNT_DETAILS()}
            <div>
                <PlayerSearch bind:player={player}/>
            </div>
            {#if player}
                <div class="option">
                    <span class="agree-terms">
                        <input name="terms" type="checkbox" bind:checked={agree_terms}/>
                    </span>
                    <div class="terms-label">
                        <a href="/{$page.params.lang}/user/terms" target="_blank">
                            {$LL.LOGIN.AGREE_TO_TERMS()}
                        </a>
                    </div>
                </div>
                <div class="option">
                    <span class="agree-terms">
                        <input name="privacy" type="checkbox" bind:checked={agree_policy}/>
                    </span>
                    <div class="terms-label">
                        <a href="/{$page.params.lang}/user/privacy-policy" target="_blank">
                            {$LL.LOGIN.AGREE_TO_PRIVACY_POLICY()}
                        </a>
                    </div>
                </div>
                <div>
                    <Button {working} on:click={transfer_account} disabled={!agree_policy || !agree_terms}>{$LL.LOGIN.TRANSFER_ACCOUNT()}</Button>
                </div>
            {/if}
        </Section>
    {:else}
        {$LL.COMMON.LOGOUT_REQUIRED()}
    {/if}
{/if}



<style>
    div {
        margin-bottom: 10px;
    }
    .option {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        margin-bottom: 10px;
    }
    span.agree-terms {
        margin-right: 10px;
    }
    .terms-label {
        text-decoration: underline;
    }
</style>