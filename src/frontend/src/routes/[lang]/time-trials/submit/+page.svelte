<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { GAMES, TRACKS_BY_GAME, ENGINE_CLASSES, type GameId, getTrackAbbreviation } from '$lib/util/gameConstants';
    import { user } from '$lib/stores/stores';
    import { check_permission, permissions } from '$lib/util/permissions';
    import type { UserInfo } from '$lib/types/user-info';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import { ArrowLeftOutline, PlusOutline } from 'flowbite-svelte-icons';

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    let selectedGame: GameId = 'mk8dx';
    let selectedTrack = '';
    let selectedCc = 150;
    let timeMinutes = '';
    let timeSeconds = '';
    let timeMilliseconds = '';
    let proofUrl = '';
    let description = '';
    let submitting = false;

    // Check if user has permission to submit time trials
    $: hasSubmitPermission = user_info?.id && check_permission(user_info, permissions.submit_time_trial, true);

    // Pre-fill from URL parameters
    onMount(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const gameParam = urlParams.get('game') as GameId;
        const trackParam = urlParams.get('track');
        const ccParam = urlParams.get('cc');

        if (gameParam && gameParam in GAMES) {
            selectedGame = gameParam;
        }
        if (trackParam && (TRACKS_BY_GAME[selectedGame] as readonly string[])?.includes(trackParam)) {
            selectedTrack = trackParam;
        }
        if (ccParam) {
            const cc = parseInt(ccParam);
            if ((ENGINE_CLASSES[selectedGame] as readonly number[])?.includes(cc)) {
                selectedCc = cc;
            }
        }
    });

    $: tracks = TRACKS_BY_GAME[selectedGame] || [];
    $: engineClasses = ENGINE_CLASSES[selectedGame] || [150];
    $: supportsEngineClass = engineClasses.length > 1;

    function handleGameChange() {
        selectedTrack = '';
        selectedCc = engineClasses[0] || 150;
    }

    function goBack() {
        const params = new URLSearchParams(window.location.search);
        const game = params.get('game');
        const track = params.get('track');
        
        if (game && track) {
            goto(`/${$page.params.lang}/time-trials/${game}/${track}`);
        } else if (game) {
            goto(`/${$page.params.lang}/time-trials/${game}`);
        } else {
            goto(`/${$page.params.lang}/time-trials`);
        }
    }

    async function submitTimeTrial() {
        if (!selectedGame || !selectedTrack || !timeMinutes || !timeSeconds || !timeMilliseconds) {
            alert('Please fill in all required fields');
            return;
        }

        // Check if user is logged in and has permission
        if (!user_info?.id) {
            alert('You must be logged in to submit time trials');
            return;
        }

        if (!hasSubmitPermission) {
            alert('You do not have permission to submit time trials');
            return;
        }

        const totalTimeMs = (parseInt(timeMinutes) * 60 * 1000) + (parseInt(timeSeconds) * 1000) + parseInt(timeMilliseconds);
        
        submitting = true;
        try {
            const timeTrialData: Record<string, number | string> = {};
            if (supportsEngineClass) {
                timeTrialData.cc = selectedCc;
            }

            const response = await fetch('/api/time-trials/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game: selectedGame,
                    track: selectedTrack,
                    time_ms: totalTimeMs,
                    data: timeTrialData,
                    proof_url: proofUrl.trim() || null,
                    description: description.trim() || null
                })
            });

            if (response.ok) {
                alert('Time trial submitted successfully!');
                const trackAbbreviation = getTrackAbbreviation(selectedGame, selectedTrack);
                goto(`/${$page.params.lang}/time-trials/${selectedGame}/${trackAbbreviation}`);
            } else {
                const error = await response.json();
                alert(`Error submitting time trial: ${error.title || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error submitting time trial:', error);
            alert('Error submitting time trial. Please try again.');
        } finally {
            submitting = false;
        }
    }
</script>

<svelte:head>
    <title>Submit Time Trial - Mario Kart Central</title>
</svelte:head>

<div class="submission-container">
    <div class="header">
        <Button color="light" on:click={goBack} extra_classes="back-button">
            <ArrowLeftOutline class="w-4 h-4 mr-2" />
            Back
        </Button>
        
        <h1 class="title">
            <PlusOutline class="w-6 h-6 mr-2" />
            Submit Time Trial
        </h1>
    </div>

    <Section>
        {#if !user_info?.id}
            <div class="permission-notice">
                <h2>Login Required</h2>
                <p>You must be logged in to submit time trials.</p>
                <Button color="primary" href="/login">
                    Login
                </Button>
            </div>
        {:else if !hasSubmitPermission}
            <div class="permission-notice">
                <h2>Permission Required</h2>
                <p>You do not have permission to submit time trials. Please contact an administrator if you believe this is an error.</p>
            </div>
        {:else}
            <form on:submit|preventDefault={submitTimeTrial} class="submission-form">
            <div class="form-group">
                <label for="game">Game *</label>
                <select 
                    id="game" 
                    bind:value={selectedGame} 
                    on:change={handleGameChange}
                    required
                >
                    {#each Object.entries(GAMES) as [gameId, gameName]}
                        <option value={gameId}>{gameName}</option>
                    {/each}
                </select>
            </div>

            <div class="form-group">
                <label for="track">Track *</label>
                <select id="track" bind:value={selectedTrack} required>
                    <option value="">Select a track...</option>
                    {#each tracks as track}
                        <option value={track}>{track}</option>
                    {/each}
                </select>
            </div>

            {#if supportsEngineClass}
                <div class="form-group">
                    <label for="cc">Engine Class *</label>
                    <select id="cc" bind:value={selectedCc} required>
                        {#each engineClasses as cc}
                            <option value={cc}>{cc}cc</option>
                        {/each}
                    </select>
                </div>
            {/if}

            <div class="form-group">
                <span class="label">Time *</span>
                <div class="time-inputs">
                    <input 
                        type="number" 
                        placeholder="MM" 
                        min="0" 
                        max="59" 
                        bind:value={timeMinutes}
                        aria-label="Minutes"
                        required
                    />
                    <span>:</span>
                    <input 
                        type="number" 
                        placeholder="SS" 
                        min="0" 
                        max="59" 
                        bind:value={timeSeconds}
                        aria-label="Seconds"
                        required
                    />
                    <span>.</span>
                    <input 
                        type="number" 
                        placeholder="mmm" 
                        min="0" 
                        max="999" 
                        bind:value={timeMilliseconds}
                        aria-label="Milliseconds"
                        required
                    />
                </div>
            </div>

            <div class="form-group">
                <span class="label">Player</span>
                <div class="player-info">
                    <span class="player-name">{user_info?.player?.name || 'Unknown'}</span>
                    <small>This time trial will be submitted under your account</small>
                </div>
            </div>

            <div class="form-group">
                <label for="proof">Proof URL (optional)</label>
                <input 
                    type="url" 
                    id="proof" 
                    bind:value={proofUrl}
                    placeholder="https://..."
                />
                <small>Video or screenshot proof of the time</small>
            </div>

            <div class="form-group">
                <label for="description">Description (optional)</label>
                <textarea 
                    id="description" 
                    bind:value={description}
                    placeholder="Additional notes about this run..."
                    rows="3"
                ></textarea>
            </div>

            <div class="form-actions">
                {#if hasSubmitPermission}
                    <Button 
                        type="submit" 
                        color="primary" 
                        disabled={submitting}
                        extra_classes="submit-button"
                    >
                        {#if submitting}
                            Submitting...
                        {:else}
                            Submit Time Trial
                        {/if}
                    </Button>
                {/if}
            </div>
            </form>
        {/if}
    </Section>
</div>

<style>
    .submission-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }

    .header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .title {
        display: flex;
        align-items: center;
        font-size: 1.75rem;
        font-weight: bold;
        color: var(--color-text-primary);
        margin: 0;
    }

    .submission-form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .form-group label,
    .form-group .label {
        font-weight: 600;
        color: var(--color-text-primary);
    }

    .form-group input,
    .form-group select,
    .form-group textarea {
        padding: 0.75rem;
        border: 1px solid var(--color-border);
        border-radius: 0.5rem;
        background: var(--color-surface);
        color: var(--color-text-primary);
        font-size: 1rem;
    }

    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px var(--color-primary-alpha);
    }

    .time-inputs {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .time-inputs input {
        width: 80px;
        text-align: center;
    }

    .time-inputs span {
        font-weight: bold;
        color: var(--color-text-secondary);
    }

    .form-group small {
        color: var(--color-text-secondary);
        font-size: 0.875rem;
    }

    .player-info {
        padding: 0.75rem;
        background: var(--color-surface-secondary);
        border-radius: 0.5rem;
        border: 1px solid var(--color-border);
    }

    .player-name {
        font-weight: 600;
        color: var(--color-text-primary);
        display: block;
        margin-bottom: 0.25rem;
    }

    .permission-notice {
        text-align: center;
        padding: 2rem;
    }

    .permission-notice h2 {
        margin: 0 0 1rem 0;
        color: var(--color-text-primary);
    }

    .permission-notice p {
        margin: 0 0 1.5rem 0;
        color: var(--color-text-secondary);
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        margin-top: 1rem;
    }

    :global(.submit-button) {
        min-width: 150px;
    }

    :global(.back-button) {
        flex-shrink: 0;
    }

    @media (max-width: 768px) {
        .header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .time-inputs {
            flex-wrap: wrap;
        }
    }
</style>
