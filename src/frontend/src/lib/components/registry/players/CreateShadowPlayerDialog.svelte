<script lang="ts">
    import Dialog from "$lib/components/common/Dialog.svelte";
    import CountrySelect from "$lib/components/common/CountrySelect.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    let player_dialog: Dialog;

    export function open() {
        player_dialog.open();
    }

    async function createPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            name: data.get('name')!.toString(),
            country_code: data.get('country')!.toString(),
            friend_codes: [],
        }
        const endpoint = '/api/registry/players/createShadowPlayer';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if(response.status < 300) {
            alert("Successfully added new shadow player");
            window.location.reload();
        }
        else {
            alert(`Adding new shadow player failed: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={player_dialog} header="Create Shadow Player">
    <form method="POST" on:submit|preventDefault={createPlayer}>
        <div class="option">
            <label for="name">Name</label>
            <input name="name" pattern="^\S.*\S$|^\S$" required/>
        </div>
        <div class="option">
            <label for="country">Country</label>
            <CountrySelect is_required/>
        </div>
        <div class="option">
            <Button type="submit">Create Player</Button>
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