<script lang='ts'>
    import LL from '$i18n/i18n-svelte';
    import type { BanInfoDetailed } from '$lib/types/ban-info';
    import BanDetails from '$lib/components/moderator/BanDetails.svelte';
    import BanPlayerForm from '$lib/components/moderator/BanPlayerForm.svelte';
    import Button from "$lib/components/common/buttons/Button.svelte";

    export let banInfo: BanInfoDetailed;

    let showBanPlayerForm : boolean = false;

    export async function unbanPlayer() {
        const confirm = window.confirm(`Are you sure you want to unban ${banInfo.player_name}?`);
        if (!confirm)
            return;

        const endpoint = `/api/registry/players/${banInfo.player_id}/ban`;
        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        });
        
        const result = await response.json();
        if (response.status < 300) {
            alert(`Successfully unbanned ${banInfo.player_name}`);
            window.location.reload();
        } 
        else {
            const detail = result.detail ? `, ${result.detail}` : '';
            alert(`${result.title}${detail}`);
        }
    };
</script>

<div>
    <BanDetails {banInfo} />
    {#if showBanPlayerForm}
        <hr/>
        <BanPlayerForm playerId={banInfo.player_id} playerName={banInfo.player_name} isEditBan handleCancel={() => {showBanPlayerForm = false}}/>
    {:else}
        <div class='button-wrapper'>
            <Button on:click={() => showBanPlayerForm = true}>{$LL.PLAYER_BAN.EDIT_BAN_DETAILS()}</Button>
            <Button color='red' on:click={unbanPlayer}>{$LL.PLAYER_BAN.UNBAN()}</Button>
        </div>
    {/if}
</div>

<style>
    hr {
        margin: 10px 0px;
    }
    .button-wrapper {
        margin-top: 10px;
    }
</style>