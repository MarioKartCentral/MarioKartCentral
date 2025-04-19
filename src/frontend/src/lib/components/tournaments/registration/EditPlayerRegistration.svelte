<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { TournamentPlayer } from "$lib/types/tournament-player";
    import TournamentStaffFields from "./TournamentStaffFields.svelte";
    import LL from "$i18n/i18n-svelte";

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
        let is_checked_in = formData.get('is_checked_in');
        let is_representative = formData.get('is_representative');
        let is_bagger_clause = formData.get('is_bagger_clause');
        let is_approved = formData.get('is_approved');
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            registration_id: player.registration_id,
            player_id: player.player_id,
            is_squad_captain: is_squad_captain !== null ? is_squad_captain === "true" : null,
            is_invite: Boolean(player.is_invite),
            is_checked_in: is_checked_in === "true",
            is_representative: is_representative !== null ? is_representative === "true" : null,
            is_bagger_clause: is_bagger_clause !== null ? is_bagger_clause === "true" : null,
            is_approved: is_approved !== null ? is_approved === "true" : null,
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
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.EDIT_REGISTRATION_FAILED()}: ${result['title']}`);
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
            registration_id: player.registration_id,
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
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.EDIT_REGISTRATION_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={edit_reg_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.EDIT_PLAYER_REGISTRATION()}>
    {#if player}
        <form method="POST" on:submit|preventDefault={is_privileged ? editRegistration : editMyRegistration}>
            <SoloTournamentFields
            {tournament}
            friend_codes={player.friend_codes}
            selected_fc_id={player.selected_fc_id}
            mii_name={player.mii_name}
            can_host={player.can_host}
            />
            {#if is_privileged}
                <TournamentStaffFields {tournament} {player} squad_exists={true}/>
            {/if}
            <div class="confirm">
                <Button type="submit">{$LL.TOURNAMENTS.REGISTRATIONS.EDIT_REGISTRATION()}</Button>
                <Button type="button" on:click={edit_reg_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
            </div>
        </form>
    {/if}
</Dialog>

<style>
    .confirm {
        margin-top: 20px;
    }
</style>