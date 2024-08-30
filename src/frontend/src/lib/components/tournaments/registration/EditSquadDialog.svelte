<script lang="ts">
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentSquad } from '$lib/types/tournament-squad';
    import SquadTournamentFields from "./SquadTournamentFields.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    
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
        const payload = {
            squad_id: squad.id,
            squad_color: Number(squad_color),
            squad_name: squad_name,
            squad_tag: squad_tag,
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
            alert(`Editing squad failed: ${result['title']}`);
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
            alert(`Editing squad failed: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={edit_squad_dialog} header="Edit Squad Registration">
    {#if squad}
        <form method="POST" on:submit|preventDefault={is_privileged ? editSquad : editMySquad}>
            <SquadTournamentFields {tournament} squad_color={squad.color} squad_name={squad.name} squad_tag={squad.tag} />
            <br />
            <div>
            <Button type="submit">Edit Squad</Button>
            <Button type="button" on:click={edit_squad_dialog.close}>Cancel</Button>
            </div>
        </form>
    {/if}
</Dialog>