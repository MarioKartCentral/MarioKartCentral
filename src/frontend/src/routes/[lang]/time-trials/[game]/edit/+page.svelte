<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { GAMES, TRACKS_BY_GAME, type GameId, getTrackAbbreviation, getTrackFromAbbreviation } from '$lib/util/gameConstants';
    import { parseTimeString, validateProofs, formatTimeMs } from '$lib/util/timeTrialUtils';
    import { user } from '$lib/stores/stores';
    import { check_permission, permissions } from '$lib/util/permissions';
    import type { UserInfo } from '$lib/types/user-info';
    import type { PlayerInfo } from '$lib/types/player-info';
    import type { TimeTrial, EditProofData, EditTimeTrialRequestData } from '$lib/types/time-trials';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import Input from '$lib/components/common/Input.svelte';
    import Section from '$lib/components/common/Section.svelte';
    import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
    import Flag from '$lib/components/common/Flag.svelte';
    import MediaEmbed from '$lib/components/media/MediaEmbed.svelte';
    import { PlusOutline, TrashBinOutline } from 'flowbite-svelte-icons';

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    // Get trial ID from URL params
    let trialId: string | null = null;
    
    // Original time trial data
    let originalTrial: TimeTrial | null = null;
    let loading = true;
    let loadError = '';

    // Form state
    let selectedGame: GameId = 'mkworld';
    let selectedTrack = '';
    let timeString = '';
    let timeError = '';
    let submitting = false;
    let submitError = '';
    let selectedPlayer: PlayerInfo | null = null;
    let showPlayerSearch = false; // Controls whether the player search is visible
    let isInvalid = false;

    // Proofs with edit-specific properties
    let proofs: (EditProofData & { id: string; isNew?: boolean })[] = [];
    const proofTypes = ['Screenshot', 'Partial Video (clip)', 'Full Video'];
    const validationStatuses = ['unvalidated', 'valid', 'invalid'];

    // --- Prepare items for NATIVE Select components ---
    $: currentTrackObjects = TRACKS_BY_GAME[selectedGame] 
        ? (TRACKS_BY_GAME[selectedGame] as readonly string[]).map(track => ({ name: track, value: track })) 
        : [];

    const proofTypeObjects = proofTypes.map(type => ({ name: type, value: type }));
    const validationStatusObjects = validationStatuses.map(status => ({ 
        name: status.charAt(0).toUpperCase() + status.slice(1), 
        value: status 
    }));

    // Permissions
    $: hasValidatePermission = user_info?.id !== null && check_permission(user_info, permissions.validate_time_trial_proof, true);
    $: canEditThisTrial = originalTrial && (
        (originalTrial.player_id === user_info?.player?.id?.toString()) || 
        hasValidatePermission
    );
    $: canChangePlayer = hasValidatePermission;
    $: canChangeValidationStatus = hasValidatePermission;
    $: canMarkInvalid = hasValidatePermission;

    // Helper function to check if a proof can be removed
    function canRemoveProof(proof: EditProofData & { isNew?: boolean }): boolean {
        // New proofs can always be removed
        if (proof.isNew) return true;
        
        // Existing proofs that are validated or invalid can only be removed by validators
        if (proof.status && ['valid', 'invalid'].includes(proof.status)) {
            return canChangeValidationStatus;
        }
        
        // Unvalidated proofs can be removed by anyone who can edit the trial
        return true;
    }

    // Helper function to check if a proof can be edited
    function canEditProof(proof: EditProofData & { isNew?: boolean }): boolean {
        // New proofs can always be edited
        if (proof.isNew) return true;
        
        // Existing proofs that are validated or invalid can only be edited by validators
        if (proof.status && ['valid', 'invalid'].includes(proof.status)) {
            return canChangeValidationStatus;
        }
        
        // Unvalidated proofs can be edited by anyone who can edit the trial
        return true;
    }

    onMount(async () => {
        trialId = $page.url.searchParams.get("trial_id");
        await loadTimeTrial();
    });

    async function loadTimeTrial() {
        try {
            loading = true;
            loadError = '';

            const response = await fetch(`/api/time-trials/${trialId}`);
            if (!response.ok) {
                const errorData = await response.json();
                loadError = errorData.title || errorData.detail || 'Failed to load time trial';
                return;
            }

            originalTrial = await response.json();
            
            if (!originalTrial) {
                loadError = 'Failed to load time trial data';
                return;
            }
            
            // Pre-populate form with existing data
            selectedGame = originalTrial.game as GameId;
            
            // Convert track abbreviation back to full name
            const fullTrackName = getTrackFromAbbreviation(selectedGame, originalTrial.track);
            selectedTrack = fullTrackName || originalTrial.track;
            
            // Format time for display
            timeString = formatTimeMs(originalTrial.time_ms);
            
            // Set up proofs
            proofs = originalTrial.proofs.map(proof => ({
                id: proof.id,
                url: proof.url,
                type: proof.type,
                status: proof.status,
                deleted: false,
                isNew: false
            }));

            // Set invalid status
            isInvalid = originalTrial.validation_status === 'invalid';

            // Set player if user can change it  
            if (canChangePlayer && originalTrial.player_name) {
                // Create a minimal PlayerInfo object for the search component
                selectedPlayer = {
                    id: parseInt(originalTrial.player_id),
                    name: originalTrial.player_name,
                    country_code: originalTrial.player_country_code || null,
                    is_hidden: false,
                    is_shadow: false,
                    is_banned: false,
                    discord: null,
                    friend_codes: [],
                    join_date: 0,
                    rosters: [],
                    ban_info: null,
                    user_settings: null,
                    name_changes: [],
                    notes: null,
                    roles: []
                };
            }

        } catch (error) {
            console.error('Error loading time trial:', error);
            loadError = 'Network error. Please check your connection and try again.';
        } finally {
            loading = false;
        }
    }

    function addProof() {
        const newId = crypto.randomUUID();
        proofs = [...proofs, { 
            id: newId, 
            url: '', 
            type: 'Screenshot', 
            deleted: false,
            isNew: true
        }];
    }

    function removeProof(id: string) {
        const proof = proofs.find(p => p.id === id);
        if (proof && !proof.isNew) {
            // Mark existing proof for deletion
            proof.deleted = true;
            proofs = [...proofs];
        } else {
            // Remove new proof entirely
            proofs = proofs.filter(p => p.id !== id);
        }
    }

    function undoDeleteProof(id: string) {
        const proof = proofs.find(p => p.id === id);
        if (proof) {
            proof.deleted = false;
            proofs = [...proofs];
        }
    }

    async function saveTimeTrial() {
        if (!originalTrial) return;

        // Clear previous errors
        timeError = '';
        submitError = '';

        // Basic validation
        if (!selectedGame || !selectedTrack || !timeString) {
            submitError = 'Please fill in all required fields, including the time.';
            return;
        }

        // Validate and parse time
        let totalTimeMs: number;
        try {
            const parsedTime = parseTimeString(timeString);
            totalTimeMs = parsedTime.totalMs;
        } catch (error) {
            timeError = error instanceof Error ? error.message : 'Invalid time format';
            return;
        }

        // Validate proofs that aren't marked for deletion
        const activeProofs = proofs.filter(p => !p.deleted && p.url && p.url.trim() !== '');
        if (activeProofs.length > 0) {
            const proofValidationErrors = validateProofs(activeProofs);
            if (proofValidationErrors.length > 0) {
                submitError = proofValidationErrors.join('; ');
                return;
            }
        }

        // Check permissions
        if (!user_info?.id) {
            submitError = 'You must be logged in to edit time trials';
            return;
        }
        if (!canEditThisTrial) {
            submitError = 'You do not have permission to edit this time trial';
            return;
        }

        submitting = true;
        try {
            // Convert selected full track name to abbreviation for backend storage
            const trackAbbreviationToSend = getTrackAbbreviation(selectedGame, selectedTrack);
            if (!trackAbbreviationToSend) {
                submitError = 'Could not determine track abbreviation. Please re-select the track.';
                return;
            }

            // Prepare proofs data for API
            const proofsToSend = proofs.map(proof => {
                const proofData: EditProofData = {
                    url: proof.url.trim(),
                    type: proof.type,
                    deleted: proof.deleted
                };

                // Include ID for existing proofs
                if (!proof.isNew) {
                    proofData.id = proof.id;
                }

                // Include status if user can validate and has set it
                if (canChangeValidationStatus && proof.status) {
                    proofData.status = proof.status;
                }

                return proofData;
            });

            // Prepare request body
            const requestBody: EditTimeTrialRequestData = {
                game: selectedGame,
                track: trackAbbreviationToSend,
                time_ms: totalTimeMs,
                proofs: proofsToSend,
                version: originalTrial.version
            };

            // Add staff-only fields
            if (canChangePlayer && selectedPlayer && selectedPlayer.id !== parseInt(originalTrial.player_id)) {
                requestBody.player_id = selectedPlayer.id;
            }

            if (canMarkInvalid) {
                requestBody.is_invalid = isInvalid;
            }

            const response = await fetch(`/api/time-trials/${trialId}/edit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                // Success - show feedback and redirect
                submitError = '';
                const successMessage = 'Time trial updated successfully! Redirecting...';
                
                const successDiv = document.createElement('div');
                successDiv.className = 'success-message bg-green-900 border border-green-700 text-green-200 px-4 py-3 rounded mb-4';
                successDiv.textContent = successMessage;
                document.querySelector('form')?.prepend(successDiv);
                
                setTimeout(() => {
                    const trackAbbreviation = getTrackAbbreviation(selectedGame, selectedTrack);
                    goto(`/${$page.params.lang}/time-trials/${selectedGame}/leaderboard?track=${trackAbbreviation}`);
                }, 1500);
            } else {
                const errorData = await response.json();
                submitError = errorData.title || errorData.detail || 'Failed to update time trial';
            }
        } catch (error) {
            console.error('Error updating time trial:', error);
            submitError = 'Network error. Please check your connection and try again.';
        } finally {
            submitting = false;
        }
    }
</script>

<svelte:head>
    <title>Edit Time Trial - Mario Kart Central</title>
</svelte:head>

{#if loading}
    <div class="loading-container text-center py-8">
        <p class="text-gray-300">Loading time trial...</p>
    </div>
{:else if loadError}
    <div class="error-container bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded mb-4">
        <h2 class="text-xl font-semibold mb-2">Error Loading Time Trial</h2>
        <p>{loadError}</p>
    </div>
{:else if !user_info?.id}
    <div class="permission-notice bg-gray-800 p-6 rounded-lg border border-gray-700 text-center mt-4 mx-auto max-w-lg">
        <h2 class="text-xl font-semibold mb-2 text-white">Login Required</h2>
        <p class="mb-4 text-gray-300">You must be logged in to edit time trials.</p>
    </div>
{:else if !canEditThisTrial}
    <div class="permission-notice bg-gray-800 p-6 rounded-lg border border-gray-700 text-center mt-4 mx-auto max-w-lg">
        <h2 class="text-xl font-semibold mb-2 text-white">Permission Required</h2>
        <p class="text-gray-300">You can only edit your own time trials. Staff members can edit any time trial.</p>
    </div>
{:else}
    <form on:submit|preventDefault={saveTimeTrial}>
        <Section header="Edit Time Trial">
            {#if submitError}
                <div class="error-message bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded mb-4">
                    {submitError}
                </div>
            {/if}
            
            <div class="option">
                <label for="game">Game *</label>
                <select id="game" bind:value={selectedGame} required disabled>
                    <option value="mkworld">{GAMES['mkworld']}</option>
                </select>
            </div>
            
            <div class="option">
                <label for="track">Track *</label>
                <div class="flex-1">
                    <select id="track" bind:value={selectedTrack} required>
                        <option value="" disabled>Select a track...</option>
                        {#each currentTrackObjects as trackOpt}
                            <option value={trackOpt.value}>{trackOpt.name}</option>
                        {/each}
                    </select>
                </div>
            </div>
            
            <div class="option">
                <label for="time">Time (e.g., 1:23.456) *</label>
                <div class="flex-1">
                    <Input 
                        type="text" 
                        id="time" 
                        name="time"
                        bind:value={timeString} 
                        placeholder="M:SS.mmm or SS.mmm"
                        required 
                        pattern={"(:?\\d{1,2}:)?\\d{1,2}\\.\\d{3}"}
                        title="Enter time as M:SS.mmm (e.g., 1:23.456) or SS.mmm (e.g., 58.123)"
                    />
                    {#if timeError}
                        <p class="text-red-400 text-sm mt-1 ml-2">{timeError}</p>
                    {/if}
                </div>
            </div>
            
            <!-- Player Information Section -->
            <div class="option">
                <span class="label-like">Player</span>
                <div class="flex-1 flex items-center gap-3">
                    {#if originalTrial?.player_country_code}
                        <Flag country_code={originalTrial.player_country_code} />
                    {/if}
                    <a 
                        href="/{$page.params.lang}/registry/players/profile?id={originalTrial?.player_id}" 
                        class="text-primary hover:underline"
                    >
                        {originalTrial?.player_name || `Player ${originalTrial?.player_id}`}
                    </a>
                    {#if canChangePlayer}
                        <Button 
                            color="primary" 
                            on:click={() => {
                                showPlayerSearch = !showPlayerSearch;
                                if (showPlayerSearch) {
                                    selectedPlayer = null; // Reset to empty when showing search
                                }
                            }}
                        >
                            Change Player
                        </Button>
                    {/if}
                </div>
            </div>
            
            {#if canChangePlayer && showPlayerSearch}
                <div class="option">
                    <label for="player">New Player</label>
                    <div class="flex-1">
                        <PlayerSearch bind:player={selectedPlayer} />
                        <p class="text-sm text-gray-400 mt-1 ml-2">Select a new player for this time trial</p>
                    </div>
                </div>
            {/if}

            {#if canMarkInvalid}
                <div class="option">
                    <label for="invalid">Invalid</label>
                    <div class="flex-1">
                        <label class="flex items-center">
                            <input type="checkbox" bind:checked={isInvalid} class="mr-2" />
                            <span class="text-sm text-gray-300">Mark this time trial as invalid</span>
                        </label>
                    </div>
                </div>
            {/if}
        </Section>

        <Section header="Proofs">
            {#if proofs.filter(p => !p.deleted).length === 0}
                <div class="option">
                    <p class="text-sm text-gray-400" style="margin-left: 0;">No proofs attached. Click below to add one.</p>
                </div>
            {/if}
            
            {#each proofs as proof (proof.id)}
                {#if proof.deleted}
                    <div class="proof-item-grouping deleted-proof" style="border: 1px solid #7f1d1d; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem; border-radius: 0.25rem; background-color: rgba(127, 29, 29, 0.1);">
                        <div class="option">
                            <span class="text-red-400">Proof marked for deletion: {proof.url || '(empty)'}</span>
                            {#if canEditProof(proof)}
                                <Button on:click={() => undoDeleteProof(proof.id)} color="alternative">
                                    Undo Delete
                                </Button>
                            {/if}
                        </div>
                    </div>
                {:else}
                    <div class="proof-item-grouping grid grid-cols-1 lg:grid-cols-2 gap-6" style="border: 1px solid #4b5563; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem; border-radius: 0.25rem;">
                        <!-- Left Column: Proof Form Fields -->
                        <div class="space-y-4">
                            <div class="option">
                                <label for={`proof-url-${proof.id}`}>Proof URL</label>
                                <Input 
                                    type="url" 
                                    id={`proof-url-${proof.id}`} 
                                    name={`proof-url-${proof.id}`}
                                    bind:value={proof.url} 
                                    placeholder="https://example.com/proof.mp4"
                                />
                            </div>
                            <div class="option">
                                <label for={`proof-type-${proof.id}`}>Type</label>
                                <select id={`proof-type-${proof.id}`} bind:value={proof.type}>
                                    {#each proofTypeObjects as typeOpt}
                                        <option value={typeOpt.value}>{typeOpt.name}</option>
                                    {/each}
                                </select>
                            </div>
                            {#if canChangeValidationStatus}
                                <div class="option">
                                    <label for={`proof-status-${proof.id}`}>Status</label>
                                    <select id={`proof-status-${proof.id}`} bind:value={proof.status}>
                                        {#each validationStatusObjects as statusOpt}
                                            <option value={statusOpt.value}>{statusOpt.name}</option>
                                        {/each}
                                    </select>
                                </div>
                            {:else}
                                <div class="option">
                                    <span class="label-like">Status</span>
                                    <span class="text-gray-300 capitalize">{proof.status || 'unvalidated'}</span>
                                </div>
                            {/if}
                            <div class="option">
                                <span style="width: 150px; margin-right: 10px;"></span>
                                {#if canRemoveProof(proof)}
                                    <Button on:click={() => removeProof(proof.id)} color="red">
                                        <TrashBinOutline class="w-4 h-4 mr-1" /> 
                                        {proof.isNew ? 'Remove' : 'Delete'}
                                    </Button>
                                {/if}
                                
                            </div>
                        </div>
                        
                        <!-- Right Column: Proof Preview -->
                        <div class="space-y-4">
                            <h4 class="text-lg font-medium border-b border-gray-600 pb-2">Proof Preview</h4>
                            
                            {#if proof.url}
                                <MediaEmbed 
                                    url={proof.url} 
                                    fallbackText="Open Proof Link"
                                    embedWidth="100%"
                                    embedHeight="300"
                                />
                                
                                <div class="text-xs text-gray-400 space-y-1">
                                    <p><strong>Type:</strong> {proof.type}</p>
                                    <p><strong>URL:</strong> <span class="break-all">{proof.url}</span></p>
                                </div>
                            {:else}
                                <div class="flex items-center justify-center h-48 bg-gray-800 rounded border border-gray-600">
                                    <p class="text-gray-400">Enter a URL to see proof preview</p>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}
            {/each}

            <div class="option">
                <Button on:click={addProof} color="primary" extra_classes="mb-2">
                    <PlusOutline class="w-4 h-4 mr-2" />
                    Add Proof
                </Button>
            </div>
        </Section>

        <Section header="Save Changes">
            <Button type="submit" color="primary" disabled={submitting}>
                {#if submitting}Saving...{:else}Save Changes{/if}
            </Button>
            <Button 
                on:click={() => window.history.back()} 
                color="alternative" 
                extra_classes="ml-2"
            >
                Cancel
            </Button>
        </Section>
    </form>
{/if}

<style>
    :global(label), .label-like {
        display: inline-block;
        width: 150px;
        margin-right: 10px;
        color: #d1d5db;
    }
    
    .option {
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }

    .flex-1 {
        flex: 1;
    }

    .error-message {
        margin-bottom: 1rem;
    }

    .permission-notice {
        margin-bottom: 1rem;
    }

    .loading-container {
        margin: 2rem 0;
    }

    .error-container {
        margin-bottom: 1rem;
    }

    .deleted-proof {
        opacity: 0.7;
    }
</style>
