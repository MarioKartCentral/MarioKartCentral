<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { TournamentPlayer } from "$lib/types/tournament-player";

    export let tournament: Tournament;
    let player: TournamentPlayer;
    let is_privileged = false;

    let edit_reg_dialog: Dialog;

    export function open(selected_player: TournamentPlayer, privileged=false) {
        player = selected_player;
        is_privileged = privileged;
        edit_reg_dialog.open();
    }

    async function editRegistration(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        let is_squad_captain = formData.get('is_squad_captain');
        let is_representative = formData.get('is_representative');
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            squad_id: player.squad_id,
            player_id: player.player_id,
            is_squad_captain: is_squad_captain !== null ? is_squad_captain === "true" : null,
            is_invite: Boolean(player.is_invite),
            is_checked_in: Boolean(player.is_checked_in),
            is_representative: is_representative !== null ? is_representative === "true" : null
        };
        const endpoint = `/api/tournaments/${tournament.id}/editRegistration`;
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

    async function editMyRegistration(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            squad_id: player.squad_id,
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
    {#if player}
        <form method="POST" on:submit|preventDefault={is_privileged ? editRegistration : editMyRegistration}>
            <SoloTournamentFields
            {tournament}
            friend_codes={player.friend_codes}
            selected_fc_id={player.selected_fc_id}
            mii_name={player.mii_name}
            can_host={player.can_host}
            />
            {#if is_privileged && player.squad_id}
                <div class="item">
                    <span class="item-label">
                        <label for="is_squad_captain">Squad captain?</label>
                    </span>
                    <select name="is_squad_captain" value={Boolean(player.is_squad_captain)} required>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
                {#if tournament.teams_only}
                    <div class="item">
                        <span class="item-label">
                            <label for="is_representative">Team representative?</label>
                        </span>
                        <select name="is_representative" value={Boolean(player.is_representative)} required>
                            <option value={false}>No</option>
                            <option value={true}>Yes</option>
                        </select>
                    </div>
                {/if}
            {/if}
            <br />
            <div>
            <Button type="submit">Edit Registration</Button>
            <Button type="button" on:click={edit_reg_dialog.close}>Cancel</Button>
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