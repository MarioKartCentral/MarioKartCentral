<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    GAMES,
    TRACKS_BY_GAME,
    type GameId,
    getTrackAbbreviation,
    getTrackFromAbbreviation,
  } from '$lib/util/gameConstants';
  import { parseTimeString, validateProofs } from '$lib/util/timeTrialUtils';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Input from '$lib/components/common/Input.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerSearch from '$lib/components/common/search/PlayerSearch.svelte';
  import { PlusOutline, TrashBinOutline } from 'flowbite-svelte-icons';
  import type { ProofRequestData } from '$lib/types/time-trials';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let selectedGame: GameId = 'mkworld';
  let selectedTrack = '';
  let timeString = '';
  let timeError = '';
  let submitting = false;
  let submitError = '';
  let selectedPlayer: PlayerInfo | null = null; // For administrators to select a different player

  let proofs: (ProofRequestData & { id: string })[] = [];
  const proofTypes = ['Screenshot', 'Partial Video (clip)', 'Full Video'];

  // Track items will be dynamically generated based on selectedGame
  $: currentTrackObjects = TRACKS_BY_GAME[selectedGame]
    ? (TRACKS_BY_GAME[selectedGame] as readonly string[]).map((track) => ({ name: track, value: track }))
    : [];

  // Proof type items are static
  const proofTypeObjects = proofTypes.map((type) => ({ name: type, value: type }));
  // ---

  $: hasSubmitPermission = user_info?.id !== null && check_permission(user_info, permissions.submit_time_trial, true);
  $: hasValidatePermission =
    user_info?.id !== null && check_permission(user_info, permissions.validate_time_trial_proof);

  onMount(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const gameParam = urlParams.get('game') as GameId;
    const trackParamFromUrl = urlParams.get('track');

    if (gameParam && gameParam === 'mkworld') {
      selectedGame = 'mkworld';
    } else {
      selectedGame = 'mkworld';
    }

    if (trackParamFromUrl) {
      let trackToSelect = '';
      const currentTracksFullNames = TRACKS_BY_GAME[selectedGame] as readonly string[];

      if (currentTracksFullNames.includes(trackParamFromUrl)) {
        trackToSelect = trackParamFromUrl;
      } else {
        const fullTrackName = getTrackFromAbbreviation(selectedGame, trackParamFromUrl);
        if (currentTracksFullNames.includes(fullTrackName)) {
          trackToSelect = fullTrackName;
        }
      }
      if (trackToSelect) {
        selectedTrack = trackToSelect;
      }
    }
  });

  function addProof() {
    proofs = [...proofs, { id: crypto.randomUUID(), url: '', type: 'Screenshot' }];
  }

  function removeProof(id: string) {
    proofs = proofs.filter((p) => p.id !== id);
  }

  async function submitTimeTrial() {
    // Clear previous errors
    timeError = '';
    submitError = '';

    // Basic validation
    if (!selectedGame || !selectedTrack || !timeString) {
      submitError = 'Please fill in all required fields, including the time.';
      return;
    }

    // Validate and parse time using utility function
    let totalTimeMs: number;
    try {
      const parsedTime = parseTimeString(timeString);
      totalTimeMs = parsedTime.totalMs;
    } catch (error) {
      timeError = error instanceof Error ? error.message : 'Invalid time format';
      return;
    }

    // Validate proofs using utility function (only if there are proofs)
    const proofsToSubmit = proofs.filter((p) => p.url && p.url.trim() !== '');
    if (proofsToSubmit.length > 0) {
      const proofValidationErrors = validateProofs(proofsToSubmit);
      if (proofValidationErrors.length > 0) {
        submitError = proofValidationErrors.join('; ');
        return;
      }
    }

    // Check user authentication and permissions
    if (user_info?.id === null) {
      submitError = 'You must be logged in to submit time trials';
      return;
    }
    if (!hasSubmitPermission) {
      submitError = 'You do not have permission to submit time trials';
      return;
    }

    submitting = true;
    try {
      const proofsToSend = proofsToSubmit.map(({ url, type }) => ({
        url: url.trim(),
        type,
      }));

      // Convert selected full track name to abbreviation for backend storage
      const trackAbbreviationToSend = getTrackAbbreviation(selectedGame, selectedTrack);
      if (!trackAbbreviationToSend) {
        submitError = 'Could not determine track abbreviation. Please re-select the track.';
        return;
      }

      // Prepare the request body
      const requestBody = {
        game: selectedGame,
        track: trackAbbreviationToSend,
        time_ms: totalTimeMs,
        proofs: proofsToSend,
        ...(selectedPlayer && selectedPlayer.id !== user_info.player?.id && { player_id: selectedPlayer.id }),
      };

      const response = await fetch('/api/time-trials/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        // Success - add visual feedback before redirect
        submitError = ''; // Clear any previous errors
        const successMessage = 'Time trial submitted successfully! Redirecting...';

        // Show success briefly before redirect
        const successDiv = document.createElement('div');
        successDiv.className =
          'success-message bg-green-900 border border-green-700 text-green-200 px-4 py-3 rounded mb-4';
        successDiv.textContent = successMessage;
        document.querySelector('form')?.prepend(successDiv);

        setTimeout(() => {
          const trackAbbreviation = getTrackAbbreviation(selectedGame, selectedTrack);
          goto(`/${$page.params.lang}/time-trials/${selectedGame}/leaderboard?track=${trackAbbreviation}`);
        }, 1500);
      } else {
        const errorData = await response.json();
        submitError = errorData.title || errorData.detail || 'Failed to submit time trial';
      }
    } catch (error) {
      console.error('Error submitting time trial:', error);
      submitError = 'Network error. Please check your connection and try again.';
    } finally {
      submitting = false;
    }
  }
</script>

{#if user_info?.id === null}
  <div class="permission-notice bg-gray-800 p-6 rounded-lg border border-gray-700 text-center mt-4 mx-auto max-w-lg">
    <h2 class="text-xl font-semibold mb-2 text-white">Login Required</h2>
    <p class="mb-4 text-gray-300">You must be logged in to submit time trials.</p>
  </div>
{:else if !hasSubmitPermission}
  <div class="permission-notice bg-gray-800 p-6 rounded-lg border border-gray-700 text-center mt-4 mx-auto max-w-lg">
    <h2 class="text-xl font-semibold mb-2 text-white">Permission Required</h2>
    <p class="text-gray-300">
      You do not have permission to submit time trials. Please contact an administrator if you believe this is an error.
    </p>
  </div>
{:else}
  <form on:submit|preventDefault={submitTimeTrial}>
    <Section header="Details">
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
        <div class="flex gap-2">
          <!-- Full track name dropdown -->
          <div class="flex-1">
            <select id="track" bind:value={selectedTrack} required>
              <option value="" disabled>Select a track...</option>
              {#each currentTrackObjects as trackOpt (trackOpt.value)}
                <option value={trackOpt.value}>{trackOpt.name}</option>
              {/each}
            </select>
          </div>
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
            pattern={'(:?\\d{1,2}:)?\\d{1,2}\\.\\d{3}'}
            title="Enter time as M:SS.mmm (e.g., 1:23.456) or SS.mmm (e.g., 58.123)"
          />
          {#if timeError}
            <p class="text-red-400 text-sm mt-1 ml-2">{timeError}</p>
          {/if}
        </div>
      </div>
      {#if hasValidatePermission}
        <div class="option">
          <label for="player">Submit for Player</label>
          <div class="flex-1">
            <PlayerSearch bind:player={selectedPlayer} showFriendCode showProfileLink isShadow={false} />
            {#if !selectedPlayer}
              <p class="text-sm text-gray-400 mt-1 ml-2">Leave empty to submit for yourself</p>
            {/if}
          </div>
        </div>
      {/if}
    </Section>

    <Section header="Proofs (Optional)">
      {#if proofs.length === 0}
        <div class="option">
          <p class="text-sm text-gray-400" style="margin-left: 0;">No proofs attached. Click below to add one.</p>
        </div>
      {/if}

      {#each proofs as proof (proof.id)}
        <div
          class="proof-item-grouping"
          style="border: 1px solid #4b5563; padding: 1rem; margin-top: 1rem; margin-bottom:1rem; border-radius: 0.25rem;"
        >
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
              {#each proofTypeObjects as typeOpt (typeOpt.value)}
                <option value={typeOpt.value}>{typeOpt.name}</option>
              {/each}
            </select>
          </div>
          <div class="option">
            <span style="width: 150px; margin-right: 10px;"></span>
            <!-- Spacer for alignment -->
            <Button on:click={() => removeProof(proof.id)} color="red">
              <TrashBinOutline class="w-4 h-4 mr-1" /> Remove
            </Button>
          </div>
        </div>
      {/each}

      <div class="option">
        <Button on:click={addProof} color="primary" extra_classes="mb-2">
          <PlusOutline class="w-4 h-4 mr-2" />
          Add Proof
        </Button>
      </div>
    </Section>

    <Section header="Submit Time">
      <Button type="submit" color="primary" disabled={submitting}>
        {#if submitting}Submitting...{:else}Submit Time{/if}
      </Button>
    </Section>
  </form>
{/if}

<style>
  /* Styles copied from /workspace/src/frontend/src/routes/[lang]/registry/teams/create/+page.svelte */
  :global(label) {
    display: inline-block;
    width: 150px;
    margin-right: 10px;
    color: #d1d5db; /* Added text-gray-300 equivalent for labels */
  }
  .option {
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start; /* Changed from center to flex-start for better error message alignment */
  }

  .flex-1 {
    flex: 1;
  }

  .error-message {
    margin-bottom: 1rem;
  }

  /* Removed .submission-container, .header, .title styles */

  /* Styles for permission notices - kept and slightly adjusted for centering */
  .permission-notice {
    /* bg-gray-800 p-6 rounded-lg border border-gray-700 text-center mt-4 */
    /* Added mx-auto and max-w-lg for centering, similar to how a form might be centered */
    margin-bottom: 1rem;
  }
</style>
