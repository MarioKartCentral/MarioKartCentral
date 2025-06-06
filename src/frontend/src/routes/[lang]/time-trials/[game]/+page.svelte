<script lang="ts">
    import { page } from '$app/stores';
    import { GAMES, TRACKS_BY_GAME, getTrackAbbreviation, type GameId } from '$lib/util/gameConstants';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import { goto } from '$app/navigation';
    import GameBadge from '$lib/components/badges/GameBadge.svelte';
    import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';

    $: game = $page.params.game as GameId;
    $: tracks = TRACKS_BY_GAME[game] || [];
    $: gameName = GAMES[game] || 'Unknown Game';

    function navigateToTrack(track: string) {
        const trackAbbr = getTrackAbbreviation(game, track);
        goto(`/${$page.params.lang}/time-trials/${game}/${trackAbbr}`);
    }
</script>

<svelte:head>
    <title>{gameName} - Time Trials - Mario Kart Central</title>
</svelte:head>

<div class="tracks-container">
    <div class="game-header">
        <div class="flex items-center gap-3">
            <GameBadge {game}/>
            <h1>{gameName} Time Trials</h1>
        </div>
        
        <SubmitButton {game} />
    </div>

    <Section header="Select a Track">
        <div class="tracks-grid">
            {#each tracks as track}
                <Button 
                    size="lg" 
                    color="light"
                    extra_classes="track-button"
                    on:click={() => navigateToTrack(track)}
                >
                    {track}
                </Button>
            {/each}
        </div>
    </Section>
</div>

<style>
    .tracks-container {
        max-width: 1200px;
        margin: 20px auto;
        padding: 0 20px;
    }

    .game-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
    }

    .game-header h1 {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }

    .tracks-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 16px;
    }

    /* Responsive design for smaller screens */
    @media (max-width: 1024px) {
        .tracks-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 768px) {
        .tracks-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 480px) {
        .tracks-grid {
            grid-template-columns: 1fr;
        }
    }

    :global(.track-button) {
        height: 60px !important;
        text-align: center;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.2;
    }
</style>
