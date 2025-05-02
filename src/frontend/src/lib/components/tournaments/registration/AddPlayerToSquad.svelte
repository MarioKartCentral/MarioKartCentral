<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import Dialog from "$lib/components/common/Dialog.svelte";
    import TournamentStaffFields from "./TournamentStaffFields.svelte";
    import type { TournamentSquad } from "$lib/types/tournament-squad";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import LL from "$i18n/i18n-svelte";
    import { game_fc_types } from "$lib/util/util";

    export let tournament: Tournament;
    let player: PlayerInfo | null = null;
    let squad: TournamentSquad;
    let working = false;

    let add_player_dialog: Dialog;

    export function open(selected_squad: TournamentSquad) {
        player = null;
        squad = selected_squad;
        add_player_dialog.open();
    }

    async function addPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if(!squad || !player) return;
        working = true;
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        let is_squad_captain = formData.get('is_squad_captain');
        let is_representative = formData.get('is_representative');
        let is_bagger_clause = formData.get('is_bagger_clause');
        let is_checked_in = formData.get('is_checked_in');
        let is_approved = formData.get('is_approved');
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            registration_id: squad.id,
            player_id: player.id,
            is_squad_captain: is_squad_captain === "true",
            is_representative: is_representative === "true",
            is_bagger_clause: is_bagger_clause === "true",
            is_checked_in: is_checked_in === "true",
            is_approved: is_approved === "true"
        };
        const endpoint = `/api/tournaments/${tournament.id}/forceRegister`;
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
            working = false;
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.ADD_PLAYER_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={add_player_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.ADD_PLAYER_TO_SQUAD()}>
    {#if squad}
        <PlayerSearch bind:player={player} fc_type={game_fc_types[tournament.game]}/>
        {#if player}
            <form method="POST" on:submit|preventDefault={addPlayer}>
                <SoloTournamentFields {tournament} friend_codes={player.friend_codes}/>
                <TournamentStaffFields {tournament} squad_exists={true}/>
                <div class="confirm">
                    <Button {working} type="submit">{$LL.TOURNAMENTS.REGISTRATIONS.ADD_PLAYER()}</Button>
                    <Button type="button" on:click={add_player_dialog.close}>{$LL.COMMON.CANCEL()}</Button>
                </div>
            </form>
        {/if}
    {/if}
</Dialog>

<style>
    .confirm {
        margin-top: 20px;
    }
</style>