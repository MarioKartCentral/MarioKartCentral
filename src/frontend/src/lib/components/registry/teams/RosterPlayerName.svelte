<script lang="ts">
    import TeamLeaderBadge from "$lib/components/badges/TeamLeaderBadge.svelte";
    import TeamManagerBadge from "$lib/components/badges/TeamManagerBadge.svelte";
    import type { RosterPlayer } from "$lib/types/roster-player";
    import { page } from "$app/stores";
    import BaggerBadge from "$lib/components/badges/BaggerBadge.svelte";

    export let player: RosterPlayer;
</script>

<span class="player {player.is_manager ? 'manager' : player.is_leader ? 'leader' : ''} {player.is_banned ? "banned_name" : ""}">
    <a href="/{$page.params.lang}/registry/players/profile?id={player.player_id}">
        {player.name}
    </a>
</span>
{#if player.is_bagger_clause}
    <BaggerBadge/>
{/if}
{#if player.is_manager}
    <TeamManagerBadge/>
{:else if player.is_leader}
    <TeamLeaderBadge/>
{/if}

<style>
    span.player {
        margin-right: 5px;
    }
    span.leader {
        color: #99e6ff;
        font-weight: bold;
    }
    span.manager {
        color: #99ff99;
        font-weight: bold;
    }
    .banned_name {
        opacity: 0.7;
        text-decoration: line-through;
    }
</style>