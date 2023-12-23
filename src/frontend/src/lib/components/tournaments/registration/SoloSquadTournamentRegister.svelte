<script lang="ts">
    import type { FriendCode } from "$lib/types/friend-code";
    import type { Tournament } from "$lib/types/tournament";
    import SoloTournamentFields from "./SoloTournamentFields.svelte";
    import SquadTournamentFields from "./SquadTournamentFields.svelte";

    export let tournament: Tournament;
    export let friend_codes: FriendCode[];

    async function registerSolo(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let selected_fc_id = formData.get("selected_fc_id");
        let mii_name = formData.get("mii_name");
        let can_host = formData.get("can_host");
        const payload = {
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === "true"
        };
        const endpoint = `/api/tournaments/${tournament.id}/register`;
        console.log(payload);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
            alert('Successfully registered for the tournament!');
        } else {
            alert(`Registration failed: ${result['title']}`);
        }
    }
    async function registerSquad(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        let squad_color = formData.get("squad_color");
        let squad_name = formData.get("squad_name");
        let squad_tag = formData.get("squad_tag");
        let selected_fc_id = formData.get("selected_fc_id");
        let mii_name = formData.get("mii_name");
        let can_host = formData.get("can_host");
        const payload = {
            squad_color: Number(squad_color),
            squad_name: squad_name,
            squad_tag: squad_tag,
            selected_fc_id: selected_fc_id ? Number(selected_fc_id) : null,
            mii_name: mii_name,
            can_host: can_host === "true"
        };
        const endpoint = `/api/tournaments/${tournament.id}/createSquad`;
        console.log(payload);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
            alert('Successfully registered for the tournament!');
        } else {
            alert(`Registration failed: ${result['title']}`);
        }
    }
</script>

<form method="POST" on:submit|preventDefault={tournament.is_squad ? registerSquad : registerSolo}>
    <SquadTournamentFields {tournament}/>
    <SoloTournamentFields {tournament} {friend_codes}/>
    
    <button type="submit">Register</button>
</form>