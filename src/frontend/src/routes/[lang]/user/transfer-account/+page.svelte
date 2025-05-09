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
                <PlayerSearch has_connected_user={false} bind:player={player}/>
            </div>
            {#if player}
                <div>
                    <Button {working} on:click={transfer_account}>{$LL.LOGIN.TRANSFER_ACCOUNT()}</Button>
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
</style>