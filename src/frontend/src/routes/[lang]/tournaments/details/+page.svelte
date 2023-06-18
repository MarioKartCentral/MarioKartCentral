<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import TournamentInfo from '$lib/components/TournamentInfo.svelte'
    import MarkdownBox from '$lib/components/MarkdownBox.svelte'
    import type { Tournament } from '$lib/types/tournament';

    let id = 0;
    let tournament_found = true;

    let tournament: Tournament;
    $: tournament_name = (tournament ? `${tournament.tournament_name}` : "Tournaments")

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);
        const res = await fetch(`/api/tournaments/${id}`);
        if(res.status !== 200) {
            tournament_found = false;
            return;
        }
        const body: Tournament = await res.json();
        tournament = body;
    });
</script>

<svelte:head>
    <title>{tournament_name} | Mario Kart Central</title>
</svelte:head>

{#if tournament}
<TournamentInfo tournament={tournament}/>
<div class="container">
    <MarkdownBox title="Tournament Details" content={tournament.description}/>
    <MarkdownBox title="Tournament Rules" content={tournament.ruleset}/>
</div>

{/if}

<style>
    .container {
        width: 50%;
        margin: 20px auto 20px auto;
    }
</style>