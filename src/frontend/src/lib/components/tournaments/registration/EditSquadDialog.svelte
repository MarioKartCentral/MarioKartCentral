<script lang="ts">
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentSquad } from '$lib/types/tournament-squad';
    import SquadTournamentFields from "./SquadTournamentFields.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";
    
    export let tournament: Tournament;
    export let is_privileged: boolean;

    let edit_squad_dialog: Dialog;
    let squad: TournamentSquad;
    
    export function open(selected_squad: TournamentSquad) {
        squad = selected_squad;
        edit_squad_dialog.open();
    }

    async function editSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let squad_color = formData.get('squad_color');
        let squad_name = formData.get('squad_name');
        let squad_tag = formData.get('squad_tag');
        let is_approved = formData.get('is_approved');
        const payload = {
            squad_id: squad.id,
            squad_color: Number(squad_color),
            squad_name: squad_name,
            squad_tag: squad_tag,
            is_approved: is_approved !== null ? is_approved === "true" : null
        };
        const endpoint = `/api/tournaments/${tournament.id}/editSquad`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD_FAILED()}: ${result['title']}`);
        }
    }

    async function editMySquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let squad_color = formData.get('squad_color');
        let squad_name = formData.get('squad_name');
        let squad_tag = formData.get('squad_tag');
        const payload = {
            squad_id: squad.id,
            squad_color: Number(squad_color),
            squad_name: squad_name,
            squad_tag: squad_tag,
        };
        const endpoint = `/api/tournaments/${tournament.id}/editMySquad`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={edit_squad_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD_REGISTRATION()}>
    {#if squad}
        <form method="POST" on:submit|preventDefault={is_privileged ? editSquad : editMySquad}>
            <SquadTournamentFields {tournament} squad_color={squad.color} squad_name={squad.name} squad_tag={squad.tag} />
            {#if is_privileged && tournament.verification_required}
                <div class="item">
                    <span class="item-label">
                        <label for="is_approved">{$LL.TOURNAMENTS.REGISTRATIONS.APPROVED_SELECT()}</label>
                    </span>
                    <select name="is_approved" value={Boolean(squad.is_approved)} required>
                        <option value={false}>{$LL.COMMON.NO()}</option>
                        <option value={true}>{$LL.COMMON.YES()}</option>
                    </select>
                </div>
            {/if}
            <div>
                <Button type="submit">{$LL.TOURNAMENTS.REGISTRATIONS.EDIT_SQUAD()}</Button>
                <Button type="button" on:click={edit_squad_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
            </div>
        </form>
    {/if}
</Dialog>

<style>
    .item-label {
        display: inline-block;
        width: 150px;
        font-weight: 525;
    }
    .item {
        margin: 10px 0;
    }
</style>