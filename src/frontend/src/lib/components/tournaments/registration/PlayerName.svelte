<script lang="ts">
    import type { TournamentPlayer } from "$lib/types/tournament-player";
    import CaptainBadge from "$lib/components/badges/CaptainBadge.svelte";
    import { page } from "$app/stores";
    import RepresentativeBadge from "$lib/components/badges/RepresentativeBadge.svelte";

    export let player: TournamentPlayer;
</script>

<div class="{player.is_squad_captain ? "captain" : player.is_representative ? "representative" : ""}">
    <a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}">
        {player.name}
    </a>
    {#if player.is_squad_captain}
        <CaptainBadge/>
    {:else if player.is_representative}
        <RepresentativeBadge/>
    {/if}
</div>

<style>
    a {
        margin-right: 5px;
    }
    .captain {
        color: #99e6ff;
        font-weight: 700;
    }
    .representative {
        color: #ffdd99;
        font-weight: 700;
    }   
</style>
