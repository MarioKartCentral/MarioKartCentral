<script lang="ts">
    import type { TournamentPlayer } from "$lib/types/tournament-player";
    import CaptainBadge from "$lib/components/badges/CaptainBadge.svelte";
    import { page } from "$app/stores";

    export let player: TournamentPlayer;
</script>

<div class="{player.is_squad_captain ? "captain" : ""}">
    <a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}">
        {player.name}
    </a>
    {#if player.is_squad_captain}
        <CaptainBadge/>
    {/if}
</div>

<style>
    .captain {
        color: #99e6ff;
        font-weight: 700;
    }   
</style>
