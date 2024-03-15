<script lang="ts">
    import type { FriendCode } from "$lib/types/friend-code";
    import type { Tournament } from "$lib/types/tournament";
    import type { MyTournamentRegistration } from "$lib/types/tournaments/my-tournament-registration";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import { Button } from "flowbite-svelte";
    import Dialog from "$lib/components/common/Dialog.svelte";

    export let tournament: Tournament;
    export let friend_codes: FriendCode[];
    export let registration: MyTournamentRegistration;

    let edit_reg_dialog: Dialog;

    export function open() {
        edit_reg_dialog.open();
    }

    async function editRegistration(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            squad_id: registration.player?.squad_id,
        };
        const endpoint = `/api/tournaments/${tournament.id}/editMyRegistration`;
        console.log(payload);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Editing registration failed: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={edit_reg_dialog} header="Edit Player Registration">
    <form method="POST" on:submit|preventDefault={editRegistration}>
    <SoloTournamentFields
      {tournament}
      {friend_codes}
      selected_fc_id={friend_codes[0].id}
      mii_name={registration.player?.mii_name}
      can_host={registration.player?.can_host}
    />
    <br />
    <div>
      <Button type="submit">Edit Registration</Button>
      <Button type="button" on:click={edit_reg_dialog.close}>Cancel</Button>
    </div>
  </form>
</Dialog>