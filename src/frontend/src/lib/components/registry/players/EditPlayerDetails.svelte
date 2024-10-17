<script lang="ts">
    import Button from "$lib/components/common/buttons/Button.svelte";
    import CountrySelect from "$lib/components/common/CountrySelect.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";

    export let player: PlayerInfo;
    export let is_privileged = false;

    let pending_change = player.name_changes.find((n) => n.approval_status === 'pending');

    async function requestNameChange(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            name: data.get('name')?.toString(),
        };
        console.log(payload);
        const endpoint = '/api/registry/players/requestName';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Requesting name change failed: ${result['title']}`);
        }
    }

    async function forceEditPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            player_id: player.id,
            name: data.get('name')?.toString(),
            country_code: data.get('country')?.toString(),
            is_hidden: data.get('is_hidden') === 'true',
            is_shadow: player.is_shadow
        };
        console.log(payload);
        const endpoint = '/api/registry/players/edit';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Editing player failed: ${result['title']}`);
        }
    }
</script>

{#if !is_privileged}
    {#if !pending_change}
        <form method="POST" on:submit|preventDefault={requestNameChange}>
            <div class="option">
                <label for="name">Name</label>
                <input name="name" value={player.name} pattern="^\S.*\S$|^\S$" required/>
            </div>
            <Button type="submit">Request Name Change</Button>
        </form>
    {:else}
        <div class="bold">
            Pending name change
        </div>
        <div>
            {player.name} -&gt; {pending_change.name}
        </div>
    {/if}
{:else}
    <form method="POST" on:submit|preventDefault={forceEditPlayer}>
        <div class="option">
            <label for="name">Display Name</label>
            <input name="name" value={player.name} pattern="^\S.*\S$|^\S$" required/>
        </div>
        <div class="option">
            <label for="country">Country</label>
            <CountrySelect value={player.country_code} is_required={true}/>
        </div>
        <div class="option">
            <label for="is_hidden">Show on player list?</label>
            <select name="is_hidden" value={player.is_hidden} required>
                <option value={false}>Show</option>
                <option value={true}>Hide</option>
            </select>
        </div>
        <Button type="submit">Edit</Button>
    </form>
{/if}

<style>
    label {
        display: inline-block;
        width: 150px;
        margin-right: 10px;
    }
    .option {
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .bold {
        font-weight: bold;
    }
</style>