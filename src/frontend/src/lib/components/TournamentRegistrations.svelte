<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentPlayer } from "$lib/types/tournament-player";
    import type { TournamentSquad } from "$lib/types/tournament-squad";
    import { onMount } from "svelte";
    import TournamentSquadList from "./TournamentSquadList.svelte";
    import TournamentPlayerList from "./TournamentPlayerList.svelte";

    export let tournament: Tournament;
    let tournament_squads: TournamentSquad[];
    let tournament_players: TournamentPlayer[];
    let registrations_loaded = false;
    //$: registration_count = (tournament_registrations ? tournament_registrations.length : 0);

    onMount(async () => {
        const res = await fetch(`/api/tournaments/${tournament.id}/registrations?`);
        const body = await res.json();
        if(tournament.is_squad) {
            tournament_squads = body;
        }
        else {
            tournament_players = body;
        }
        registrations_loaded = true;
    });
</script>

<div>
    <b>Tournament Registrations</b>
    {#if registrations_loaded}
        {#if tournament.is_squad}
            <TournamentSquadList tournament={tournament} squads={tournament_squads}/>
        {:else}
            <TournamentPlayerList tournament={tournament} players={tournament_players}/>
        {/if}
    {/if}
</div>
