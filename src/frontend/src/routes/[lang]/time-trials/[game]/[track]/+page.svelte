<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { GAMES, ENGINE_CLASSES, type GameId } from '$lib/util/gameConstants';
    import type { TimeTrial } from '$lib/types/time-trials';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import PageNavigation from '$lib/components/common/PageNavigation.svelte';
    import GameBadge from '$lib/components/badges/GameBadge.svelte';
    import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
    import { ArrowLeftOutline } from 'flowbite-svelte-icons';

    export let data;
    
    $: game = data.game as GameId;
    $: track = data.track;
    $: trackAbbr = data.trackAbbr;
    $: initialCc = data.cc;
    $: gameName = GAMES[game] || 'Unknown Game';
    $: engineClasses = ENGINE_CLASSES[game] || [150];
    $: supportsEngineClass = engineClasses?.length > 1;
    
    // Ensure selectedCc is always valid for the current game
    $: if (engineClasses && !(engineClasses as readonly number[]).includes(selectedCc)) {
        selectedCc = initialCc && (engineClasses as readonly number[]).includes(initialCc) ? initialCc : engineClasses[0] || 150;
    }

    let currentPage = 1;
    let totalPages = 1;
    let timeTrials: TimeTrial[] = [];
    let selectedCc = 150; // Initialize with a safe default
    let loading = false;

    const PAGE_SIZE = 100;

    function formatTime(timeMs: number): string {
        const minutes = Math.floor(timeMs / 60000);
        const seconds = Math.floor((timeMs % 60000) / 1000);
        const milliseconds = timeMs % 1000;
        
        if (minutes > 0) {
            return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
        } else {
            return `${seconds}.${milliseconds.toString().padStart(3, '0')}`;
        }
    }

    async function fetchLeaderboard() {
        loading = true;
        try {
            let url = `/api/time-trials/list?game=${encodeURIComponent(game)}&track=${encodeURIComponent(trackAbbr)}&limit=${PAGE_SIZE}&offset=${(currentPage - 1) * PAGE_SIZE}`;
            
            if (supportsEngineClass) {
                url += `&cc=${selectedCc}`;
            }

            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                timeTrials = data;
                // For now, assume we have at least one full page if we get 100 results
                totalPages = data.length === PAGE_SIZE ? currentPage + 1 : currentPage;
            } else {
                console.error('Failed to fetch leaderboard:', response.statusText);
                timeTrials = [];
            }
        } catch (error) {
            console.error('Error fetching leaderboard:', error);
            timeTrials = [];
        } finally {
            loading = false;
        }
    }

    function changeEngineClass(cc: number) {
        selectedCc = cc;
        currentPage = 1;
        const url = new URL(window.location.href);
        url.searchParams.set('cc', cc.toString());
        goto(url.toString(), { replaceState: true });
        fetchLeaderboard();
    }

    function goBack() {
        goto(`/${$page.params.lang}/time-trials/${game}`);
    }

    onMount(() => {
        // Set the initial selected CC based on URL parameter or default to first available engine class
        if (initialCc && (engineClasses as readonly number[]).includes(initialCc)) {
            selectedCc = initialCc;
        } else if (engineClasses && engineClasses.length > 0) {
            selectedCc = engineClasses[0];
        } else {
            selectedCc = 150; // Fallback
        }
        fetchLeaderboard();
    });
</script>

<svelte:head>
    <title>{track} - {gameName} - Time Trials - Mario Kart Central</title>
</svelte:head>

<div class="leaderboard-container">
    <div class="header">
        <Button color="light" on:click={goBack} extra_classes="back-button">
            <ArrowLeftOutline class="w-4 h-4 mr-2" />
            Back to {gameName}
        </Button>
        
        <div class="track-header">
            <GameBadge {game}/>
            <div>
                <h1>{track}</h1>
                <p class="game-subtitle">{gameName}</p>
            </div>
        </div>
        
        <SubmitButton {game} track={trackAbbr} />
    </div>

    {#if supportsEngineClass}
        <div class="engine-class-selector">
            {#each engineClasses as cc}
                <Button 
                    color={selectedCc === cc ? 'blue' : 'light'}
                    size="sm"
                    on:click={() => changeEngineClass(cc)}
                >
                    {cc}cc
                </Button>
            {/each}
        </div>
    {/if}

    <Section header="Leaderboard">
        {#if loading}
            <div class="loading">Loading...</div>
        {:else if timeTrials.length === 0}
            <div class="no-results">No time trials found for this track.</div>
        {:else}
            <div class="leaderboard-table">
                <div class="table-header">
                    <div class="rank-col">Rank</div>
                    <div class="player-col">Player</div>
                    <div class="time-col">Time</div>
                    <div class="date-col">Date</div>
                </div>
                
                {#each timeTrials as timeTrial, index}
                    <div class="table-row">
                        <div class="rank-col">#{(currentPage - 1) * PAGE_SIZE + index + 1}</div>
                        <div class="player-col">
                            <div class="player-info">
                                <!-- TODO: Add country flag based on player data -->
                                <span class="player-name">{timeTrial.player_id}</span>
                            </div>
                        </div>
                        <div class="time-col">
                            <span class="time">{formatTime(timeTrial.time_ms)}</span>
                        </div>
                        <div class="date-col">
                            {new Date(timeTrial.created_at).toLocaleDateString()}
                        </div>
                    </div>
                {/each}
            </div>

            {#if totalPages > 1}
                <PageNavigation 
                    bind:currentPage 
                    {totalPages} 
                    refresh_function={fetchLeaderboard}
                />
            {/if}
        {/if}
    </Section>
</div>

<style>
    .leaderboard-container {
        max-width: 1200px;
        margin: 20px auto;
        padding: 0 20px;
    }

    .header {
        margin-bottom: 24px;
    }

    .track-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 16px;
    }

    .track-header h1 {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }

    .game-subtitle {
        color: #666;
        margin: 4px 0 0 0;
        font-size: 0.9rem;
    }

    .engine-class-selector {
        display: flex;
        gap: 8px;
        margin-bottom: 24px;
    }

    .loading, .no-results {
        text-align: center;
        padding: 40px;
        color: #666;
        font-style: italic;
    }

    .leaderboard-table {
        width: 100%;
    }

    .table-header, .table-row {
        display: grid;
        grid-template-columns: 80px 1fr 120px 120px;
        gap: 16px;
        padding: 12px 16px;
        align-items: center;
    }

    .table-header {
        background-color: #f8f9fa;
        font-weight: bold;
        border-bottom: 2px solid #dee2e6;
        border-radius: 8px 8px 0 0;
    }

    .table-row {
        border-bottom: 1px solid #dee2e6;
        transition: background-color 0.2s;
    }

    .table-row:hover {
        background-color: #f8f9fa;
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .rank-col {
        font-weight: bold;
        color: #666;
    }

    .player-info {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .player-name {
        font-weight: 500;
    }

    .time {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 1.1rem;
        color: #0066cc;
    }

    .date-col {
        color: #666;
        font-size: 0.9rem;
    }

    :global(.back-button) {
        margin-bottom: 8px;
    }

    .header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }

    .track-header {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
        min-width: 0;
    }

    .track-header h1 {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
        color: var(--color-text-primary);
    }

    .game-subtitle {
        color: var(--color-text-secondary);
        margin: 0;
        font-size: 0.9rem;
    }

    @media (max-width: 768px) {
        .leaderboard-container {
            padding: 0 12px;
        }

        .header {
            flex-direction: column;
            align-items: stretch;
            gap: 1rem;
        }

        .table-header, .table-row {
            grid-template-columns: 60px 1fr 100px;
            gap: 8px;
            padding: 8px 12px;
        }

        .date-col {
            display: none;
        }

        .track-header h1 {
            font-size: 1.5rem;
        }
    }
</style>
