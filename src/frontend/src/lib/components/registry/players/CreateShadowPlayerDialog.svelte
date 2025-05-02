<script lang="ts">
    import Dialog from "$lib/components/common/Dialog.svelte";
    import CountrySelect from "$lib/components/common/CountrySelect.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";

    let player_dialog: Dialog;
    let working = false;

    export function open() {
        player_dialog.open();
    }

    async function createPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        working = true;
        const data = new FormData(event.currentTarget);
        const payload = {
            name: data.get('shadow_name')!.toString(),
            country_code: data.get('country')!.toString(),
            friend_codes: [],
        }
        const endpoint = '/api/registry/players/createShadowPlayer';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        working = false;
        const result = await response.json();
        if(response.status < 300) {
            alert($LL.PLAYERS.SHADOW_PLAYERS.CREATE_SHADOW_PLAYER_SUCCESS());
            window.location.reload();
        }
        else {
            alert(`${$LL.PLAYERS.SHADOW_PLAYERS.CREATE_SHADOW_PLAYER_FAILURE()}: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={player_dialog} header={$LL.PLAYERS.SHADOW_PLAYERS.CREATE_SHADOW_PLAYER()}>
    <form method="POST" on:submit|preventDefault={createPlayer}>
        <div class="option">
            <label for="shadow_name">{$LL.COMMON.NAME()}</label>
            <input name="shadow_name" required/>
        </div>
        <div class="option">
            <label for="country">{$LL.COMMON.COUNTRY()}</label>
            <CountrySelect is_required/>
        </div>
        <div class="option">
            <Button {working} type="submit">{$LL.PLAYERS.SHADOW_PLAYERS.CREATE_SHADOW_PLAYER()}</Button>
        </div>
    </form>
</Dialog>

<style>
    label {
        display: inline-block;
        width: 100px;
    }
    .option {
        margin-bottom: 10px;
    }
</style>