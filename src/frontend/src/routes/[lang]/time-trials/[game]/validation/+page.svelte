<!-- Simplified MVP Validation Page -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { ProofWithValidationStatusResponseData, ErrorResponse } from '$lib/types/time-trials';
  import LL from '$i18n/i18n-svelte';
  import { check_permission, permissions } from '$lib/util/permissions';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import MediaEmbed from '$lib/components/media/MediaEmbed.svelte';
  import { getTrackFromAbbreviation, TRACKS_BY_GAME, type GameId } from '$lib/util/gameConstants';
  import { ArrowLeftOutline } from 'flowbite-svelte-icons';

  let proofsForValidation: ProofWithValidationStatusResponseData[] = [];
  let isLoading = true;
  let errorMessage: string | null = null;
  let gameFilter: string | null = null;
  let hasValidationPermission = false;
  let hasFetchedOnce = false;

  let proofValidationState: Record<
    string,
    {
      isSubmitting: boolean;
    }
  > = {};

  // Use reactive statement to check permissions
  $: hasValidationPermission = Boolean(
    $user?.id !== null && check_permission($user, permissions.validate_time_trial_proof),
  );

  // Track conversion helper
  function getFullTrackName(game: string, track: string): string {
    if (!track) return '';
    const gameId = game as GameId;
    if (gameId in TRACKS_BY_GAME) {
      const fullName = getTrackFromAbbreviation(gameId, track);
      return fullName !== track ? fullName : track;
    }
    return track;
  }

  onMount(async () => {
    gameFilter = $page.params.game ?? null;
    isLoading = true;
  });

  // Watch for permission changes and fetch data when permissions are granted
  $: if (hasValidationPermission && gameFilter && !hasFetchedOnce) {
    fetchProofsForValidation();
  }

  // If we don't have permissions but user is loaded, stop loading
  $: if ($user !== undefined && !hasValidationPermission) {
    isLoading = false;
  }

  async function fetchProofsForValidation() {
    isLoading = true;
    hasFetchedOnce = true;
    errorMessage = null;
    try {
      const response = await fetch(`/api/time-trials/proofs/validation-queue`);
      if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({ detail: $LL.TIME_TRIALS.LOAD_ERROR() }));
        throw new Error(errorData.detail || $LL.TIME_TRIALS.LOAD_ERROR());
      }
      const data = await response.json();
      if (data && data.proofs) {
        // Filter proofs by game on the client side
        proofsForValidation = data.proofs.filter((p: ProofWithValidationStatusResponseData) =>
          gameFilter ? p.game === gameFilter : true,
        );
      } else {
        proofsForValidation = [];
      }
    } catch (error: unknown) {
      errorMessage = error instanceof Error ? error.message : $LL.TIME_TRIALS.UNEXPECTED_ERROR();
      console.error(error);
    } finally {
      isLoading = false;
    }
  }

  // Simplified validation functions for MVP
  async function markProofAsValid(proof: ProofWithValidationStatusResponseData) {
    if (!proofValidationState[proof.id]) {
      proofValidationState[proof.id] = { isSubmitting: false };
    }

    const state = proofValidationState[proof.id];

    state.isSubmitting = true;
    proofValidationState = proofValidationState;

    try {
      // MVP: Use new mark-valid endpoint with trial_id and proof_id
      const response = await fetch(`/api/time-trials/${proof.time_trial_id}/proofs/${proof.id}/mark-valid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ version: proof.version }),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response
          .json()
          .catch(() => ({ detail: $LL.TIME_TRIALS.UNKNOWN_ERROR_ALERT() }));
        if (response.status === 409) {
          throw new Error('This record was modified by another user. Please refresh the page and try again.');
        }
        throw new Error(errorData.detail || 'Failed to mark proof as valid');
      }

      // Refresh the validation queue data
      await fetchProofsForValidation();
    } catch (error) {
      console.error('Error marking proof as valid:', error);
      alert(error instanceof Error ? error.message : 'An error occurred while marking the proof as valid.');
    } finally {
      if (proofValidationState[proof.id]) {
        proofValidationState[proof.id].isSubmitting = false;
        proofValidationState = proofValidationState;
      }
    }
  }

  async function markProofAsInvalid(proof: ProofWithValidationStatusResponseData) {
    if (!proofValidationState[proof.id]) {
      proofValidationState[proof.id] = { isSubmitting: false };
    }

    const state = proofValidationState[proof.id];

    state.isSubmitting = true;
    proofValidationState = proofValidationState;

    try {
      // Use the new endpoint with trial_id and proof_id to mark the entire proof as invalid
      const response = await fetch(`/api/time-trials/${proof.time_trial_id}/proofs/${proof.id}/mark-invalid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ version: proof.version }),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response
          .json()
          .catch(() => ({ detail: $LL.TIME_TRIALS.UNKNOWN_ERROR_ALERT() }));
        if (response.status === 409) {
          throw new Error('This record was modified by another user. Please refresh the page and try again.');
        }
        throw new Error(errorData.detail || 'Failed to mark proof as invalid');
      }

      // Refresh the validation queue data
      await fetchProofsForValidation();
    } catch (error) {
      console.error('Error marking proof as invalid:', error);
      alert(error instanceof Error ? error.message : 'An error occurred while marking the proof as invalid.');
    } finally {
      if (proofValidationState[proof.id]) {
        proofValidationState[proof.id].isSubmitting = false;
        proofValidationState = proofValidationState;
      }
    }
  }

  async function markTimeTrialAsInvalid(proof: ProofWithValidationStatusResponseData) {
    if (!proofValidationState[proof.id]) {
      proofValidationState[proof.id] = { isSubmitting: false };
    }

    const state = proofValidationState[proof.id];

    state.isSubmitting = true;
    proofValidationState = proofValidationState;

    try {
      // Use the new endpoint to mark the entire time trial record as invalid
      const response = await fetch(`/api/time-trials/${proof.time_trial_id}/mark-invalid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ version: proof.version }),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response
          .json()
          .catch(() => ({ detail: $LL.TIME_TRIALS.UNKNOWN_ERROR_ALERT() }));
        if (response.status === 409) {
          throw new Error('This record was modified by another user. Please refresh the page and try again.');
        }
        throw new Error(errorData.detail || 'Failed to mark time trial as invalid');
      }

      // Refresh the validation queue data
      await fetchProofsForValidation();
    } catch (error) {
      console.error('Error marking time trial as invalid:', error);
      alert(error instanceof Error ? error.message : 'An error occurred while marking the time trial as invalid.');
    } finally {
      if (proofValidationState[proof.id]) {
        proofValidationState[proof.id].isSubmitting = false;
        proofValidationState = proofValidationState;
      }
    }
  }
</script>

<svelte:head>
  <title>{$LL.TIME_TRIALS.VALIDATION_PAGE_TITLE()} | MKCentral</title>
</svelte:head>

<div class="container mx-auto p-4">
  <Button href="/{$page.params.lang}/time-trials/{gameFilter}" extra_classes="back-button text-white mb-4">
    <ArrowLeftOutline class="w-4 h-4 mr-2" />
    {$LL.TIME_TRIALS.BACK_TO_GAME_HOMEPAGE()}
  </Button>
  <h1 class="text-2xl font-bold mb-4">{$LL.TIME_TRIALS.VALIDATION_HEADER()}</h1>

  {#if $user === undefined}
    <div class="text-center py-8">
      <p class="text-lg">Loading...</p>
    </div>
  {:else if !hasValidationPermission}
    <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded text-center">
      <h2 class="text-xl font-semibold mb-2">{$LL.TIME_TRIALS.PERMISSION_REQUIRED()}</h2>
      <p>{$LL.TIME_TRIALS.NO_PERMISSION_MESSAGE()}</p>
    </div>
  {:else if isLoading}
    <div class="text-center py-8">
      <p class="text-lg">Loading...</p>
    </div>
  {:else if errorMessage}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      <p>{errorMessage}</p>
    </div>
  {:else if proofsForValidation.length === 0}
    <div class="text-center py-8">
      <p class="text-lg text-base-content/60">
        {$LL.TIME_TRIALS.NO_PROOFS_PENDING_FOR_GAME({
          game: gameFilter || $LL.TIME_TRIALS.VALIDATION_GAME_FILTER_ALL(),
        })}
      </p>
    </div>
  {:else}
    <div class="space-y-6">
      {#each proofsForValidation as proof (proof.id)}
        <div class="proof-item overflow-hidden">
          <!-- Proof Header -->
          <div class="bg-base-200 px-6 py-4 border-b border-base-300">
            <div class="flex items-center justify-between">
              <a
                href="/{$page.params.lang}/registry/players/profile?id={proof.player_id}"
                class="text-lg font-semibold text-primary hover:underline"
              >
                <div class="flex items-center gap-3">
                  {#if proof.player_country_code}
                    <Flag country_code={proof.player_country_code} />
                  {/if}

                  {proof.player_name || proof.player_id}
                  <span class="text-sm text-base-content/60">
                    {new Date(proof.created_at).toLocaleDateString()}
                  </span>
                </div>
              </a>
              <div class="text-right text-sm">
                <div class="font-medium">{getFullTrackName(gameFilter || '', proof.track || '')}</div>
                {#if proof.time_ms}
                  <div class="text-base-content/70">
                    {Math.floor(proof.time_ms / 60000)}:{Math.floor((proof.time_ms % 60000) / 1000)
                      .toString()
                      .padStart(2, '0')}.{(proof.time_ms % 1000).toString().padStart(3, '0')}
                  </div>
                {/if}
              </div>
            </div>
          </div>

          <!-- Two Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
            <!-- Left Column: Simple Validation Actions -->
            <div class="space-y-4">
              <h3 class="text-lg font-medium border-b border-base-300 pb-2">Validation Actions</h3>

              <div class="space-y-3">
                <!-- Track and Time Display (Read-only for MVP) -->
                <div>
                  <div class="text-sm font-medium text-base-content/70">Track:</div>
                  <div class="text-lg">{getFullTrackName(gameFilter || '', proof.track || '')}</div>
                </div>

                {#if proof.time_ms}
                  <div>
                    <div class="text-sm font-medium text-base-content/70">Time:</div>
                    <div class="text-lg font-mono">
                      {Math.floor(proof.time_ms / 60000)}:{Math.floor((proof.time_ms % 60000) / 1000)
                        .toString()
                        .padStart(2, '0')}.{(proof.time_ms % 1000).toString().padStart(3, '0')}
                    </div>
                  </div>
                {/if}
              </div>

              <!-- Simple Validation Actions -->
              <div class="pt-4 border-t border-base-300 space-y-3">
                <div class="flex gap-2">
                  <Button
                    color="green"
                    size="lg"
                    disabled={proofValidationState[proof.id]?.isSubmitting || false}
                    on:click={() => markProofAsValid(proof)}
                    extra_classes="flex-1"
                  >
                    {proofValidationState[proof.id]?.isSubmitting ? 'Processing...' : '✓ Mark Proof Valid'}
                  </Button>
                  <Button
                    color="yellow"
                    size="lg"
                    disabled={proofValidationState[proof.id]?.isSubmitting || false}
                    on:click={() => markProofAsInvalid(proof)}
                    extra_classes="flex-1"
                  >
                    {proofValidationState[proof.id]?.isSubmitting ? 'Processing...' : '⚠ Mark Proof Invalid'}
                  </Button>
                  <Button
                    color="red"
                    size="lg"
                    disabled={proofValidationState[proof.id]?.isSubmitting || false}
                    on:click={() => markTimeTrialAsInvalid(proof)}
                    extra_classes="flex-1"
                  >
                    {proofValidationState[proof.id]?.isSubmitting ? 'Processing...' : '❌ Mark Record Invalid'}
                  </Button>
                </div>
                <p class="text-xs text-base-content/70 text-center">
                  <strong>Mark Proof Valid:</strong> Proof correctly shows track/time.
                  <strong>Mark Proof Invalid:</strong> Broken link, wrong content.
                  <strong>Mark Record Invalid:</strong> Obviously fake/impossible time.
                </p>
              </div>
            </div>

            <!-- Right Column: Proof Evidence Preview -->
            <div class="space-y-4">
              <h3 class="text-lg font-medium border-b border-base-300 pb-2">Proof Evidence</h3>

              {#if proof.proof_data?.url}
                <MediaEmbed
                  url={proof.proof_data.url}
                  fallbackText="Open Proof Link"
                  embedWidth="100%"
                  embedHeight="400"
                />

                <div class="text-xs text-base-content/60 space-y-1 mt-4">
                  <p><strong>Type:</strong> {proof.proof_data?.type || 'N/A'}</p>
                  <p><strong>URL:</strong> <span class="break-all">{proof.proof_data.url}</span></p>
                </div>
              {:else}
                <div class="flex items-center justify-center h-48 bg-base-200 rounded-lg">
                  <p class="text-base-content/60">{$LL.TIME_TRIALS.NO_EVIDENCE_PROVIDED()}</p>
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .proof-item {
    background-color: rgba(235, 255, 255, 0.1);
  }
</style>
