<script lang="ts">
    import { page } from '$app/stores';
    import { GAMES, TRACKS_BY_GAME, getTrackAbbreviation, type GameId } from '$lib/util/gameConstants';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import { goto } from '$app/navigation';
    import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
    import { ArrowLeftOutline, BadgeCheckOutline } from 'flowbite-svelte-icons';
    import { user } from '$lib/stores/stores';
    import { check_permission, permissions } from '$lib/util/permissions';
    import LL from '$i18n/i18n-svelte';

    $: game = $page.params.game as GameId;
    $: tracks = TRACKS_BY_GAME[game] || [];
    $: gameName = GAMES[game] || 'Unknown Game';

    function navigateToTrack(track: string) {
        const trackAbbr = getTrackAbbreviation(game, track);
        goto(`/${$page.params.lang}/time-trials/${game}/leaderboard?track=${trackAbbr}`);
    }

    function goBackToGameList() {
        goto(`/${$page.params.lang}/time-trials`);
    }

    function navigateToValidation() {
        goto(`/${$page.params.lang}/time-trials/${game}/validation`);
    }

    function navigateToLeaderboard() {
        goto(`/${$page.params.lang}/time-trials/${game}/leaderboard`);
    }
</script>

<svelte:head>
    <title>{gameName} - Time Trials - Mario Kart Central</title>
</svelte:head>

<div class="tracks-container">
    <Button on:click={goBackToGameList} extra_classes="back-button text-white mb-4">
        <ArrowLeftOutline class="w-4 h-4 mr-2" />
        Back to All Games
    </Button>

    <div class="game-header">
        <div class="flex items-center gap-3">
            <h1 class="text-white">{gameName} Time Trials</h1>
        </div>
        
        <div class="flex items-center gap-2">
            <Button on:click={navigateToLeaderboard} size='md' extra_classes="flex items-center">
                🏆 {$LL.TIME_TRIALS.LEADERBOARDS()}
            </Button>
            <SubmitButton {game} />
            {#if $user && check_permission($user, permissions.validate_time_trial_proof)}
                <Button on:click={navigateToValidation} color="blue" size='md' extra_classes="flex items-center">
                    <BadgeCheckOutline class="w-5 h-5 mr-2" />
                    {$LL.TIME_TRIALS.VALIDATE_PROOFS_BUTTON()}
                </Button>
            {/if}
        </div>
    </div>

    <Section header="Select a Track">
        <div class="tracks-grid">
            {#each tracks as track}
                <Button 
                    size="lg" 
                    extra_classes="track-button border-gray-600 hover:bg-gray-500 text-white"
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
        background-color: rgba(255, 255, 255, 0.12);
    }
    :global(.track-button:hover) {
        background-color: rgba(255, 255, 255, 0.2);
    }
</style>
