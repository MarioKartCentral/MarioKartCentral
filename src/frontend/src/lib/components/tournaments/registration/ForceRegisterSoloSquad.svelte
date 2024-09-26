<script lang="ts">
    import type { PlayerInfo } from "$lib/types/player-info";
    import type { Tournament } from "$lib/types/tournament";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import SquadTournamentFields from "./SquadTournamentFields.svelte";
    import PlayerSearch from "$lib/components/common/PlayerSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import TournamentStaffFields from "./TournamentStaffFields.svelte";

    export let tournament: Tournament;
    let player: PlayerInfo | null;

    async function registerSolo(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if(!player) return;
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        const payload = {
            player_id: player.id,
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true'    
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
            alert('Successfully registered this player for the tournament!');
        } else {
            alert(`Registration failed: ${result['title']}`);
        }
    }
    async function registerSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if(!player) return;
        const formData = new FormData(event.currentTarget);
        let squad_color = formData.get('squad_color');
        let squad_name = formData.get('squad_name');
        let squad_tag = formData.get('squad_tag');
        let selected_fc_id = formData.get('selected_fc_id');
        let mii_name = formData.get('mii_name');
        let can_host = formData.get('can_host');
        let is_bagger_clause = formData.get('is_bagger_clause');
        const payload = {
            player_id: player.id,
            squad_color: Number(squad_color),
            squad_name: squad_name,
            squad_tag: squad_tag,
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === 'true',
            is_bagger_clause: is_bagger_clause === 'true',
        };
        const endpoint = `/api/tournaments/${tournament.id}/forceCreateSquad`;
        console.log(payload);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
            alert('Successfully registered this player for the tournament!');
        } else {
            alert(`Registration failed: ${result['title']}`);
        }
    }
</script>

<div class="manual-register">
    <div>Manually Register {tournament.is_squad ? "Squad" : "Player"}</div>
    <PlayerSearch bind:player={player} game={tournament.game}/>
    {#if player}
        <form method="POST" on:submit|preventDefault={tournament.is_squad ? registerSquad : registerSolo}>
            <SquadTournamentFields {tournament}/>
            <SoloTournamentFields {tournament} friend_codes={player.friend_codes}/>
            <TournamentStaffFields {tournament}/>
            <Button type="submit">Register</Button>
        </form>
    {/if}
</div>

<style>
    .manual-register {
        margin-top: 20px;
    }
  </style>
  