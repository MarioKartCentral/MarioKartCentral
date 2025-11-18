<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { formatTime } from '$lib/utils/time';
  import LL from '$i18n/i18n-svelte';
  import { MKWORLD_TRACK_ABBREVIATIONS, MKWORLD_TRACK_TRANSLATION_IDS, type GameId } from '$lib/util/gameConstants';
  import {
    XCompanySolid,
    YoutubeSolid,
    CameraFotoSolid,
    VideoCameraSolid,
    ArrowLeftOutline,
    ChevronDownOutline,
  } from 'flowbite-svelte-icons';
  import Twitch from '$lib/components/icons/Twitch.svelte';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import MediaEmbed from '$lib/components/media/MediaEmbed.svelte';
  import { Popover } from 'flowbite-svelte';
  import type { TimeTrial, TimeTrialListResponse } from '$lib/types/time-trials';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';

  const game = $page.params.game as GameId;

  let records: TimeTrial[] = [];
  let loading = true;
  let error = '';
  let selectedTrack = '';
  let selectedCountry = '';
  let showPendingValidation = false;
  let showTimesWithoutProof = false;
  let tracks: string[] = [];
  let countries: string[] = [];

  async function loadLeaderboard() {
    // Don't load if no track is selected or if running during SSR
    if (!selectedTrack || typeof window === 'undefined') {
      return;
    }

    try {
      loading = true;
      error = '';

      const params = new URLSearchParams({
        game: game,
        track: selectedTrack,
        limit: '50',
      });

      // Add validation status filters based on checkbox states
      if (showPendingValidation) {
        params.append('include_unvalidated', 'true');
      }
      if (showTimesWithoutProof) {
        params.append('include_proofless', 'true');
      }

      const response = await fetch(`/api/time-trials/leaderboard?${params}`);

      if (!response.ok) {
        throw new Error(`Failed to load leaderboard: ${response.statusText}`);
      }

      const result: TimeTrialListResponse = await response.json();
      let allRecords = result['records'] || [];

      // Client-side filtering
      let filteredRecords = allRecords;

      // Filter by country if selected
      if (selectedCountry) {
        filteredRecords = filteredRecords.filter((record) => record.player_country_code === selectedCountry);
      }

      // Convert back to array and sort by time
      records = filteredRecords;

      // Extract unique countries for the dropdown (from all records, not just filtered ones)
      const uniqueCountries = [
        ...new Set(
          allRecords
            .map((record) => record.player_country_code)
            .filter((country): country is string => country != null && country.trim() !== ''),
        ),
      ].sort();
      countries = uniqueCountries;
    } catch (err) {
      console.error('Error loading leaderboard:', err);
      error = err instanceof Error ? err.message : 'Failed to load leaderboard';
    } finally {
      loading = false;
    }
  }

  function getGameDisplayName(gameId: string): string {
    const upperGame = gameId?.toUpperCase();
    if (upperGame && $LL.GAMES[upperGame as keyof typeof $LL.GAMES]) {
      return $LL.GAMES[upperGame as keyof typeof $LL.GAMES]();
    }
    return gameId?.toUpperCase() || 'Game';
  }

  function getCountryDisplayName(countryCode: string | null): string | null {
    if (countryCode && $LL.COUNTRIES[countryCode as keyof typeof $LL.COUNTRIES]) {
      return $LL.COUNTRIES[countryCode as keyof typeof $LL.COUNTRIES]();
    }
    return countryCode;
  }

  function getTrackDisplayName(trackAbbr: string): string {
    if (game === 'mkworld') {
      // Find the full name for this abbreviation
      const fullName = Object.keys(MKWORLD_TRACK_ABBREVIATIONS).find(
        (name) => MKWORLD_TRACK_ABBREVIATIONS[name] === trackAbbr,
      );
      const nameId = MKWORLD_TRACK_TRANSLATION_IDS[fullName as keyof typeof MKWORLD_TRACK_TRANSLATION_IDS];
      const translatedName = $LL.MARIO_KART_WORLD.TRACKS[nameId as keyof typeof $LL.MARIO_KART_WORLD.TRACKS]();
      return translatedName || fullName || trackAbbr;
    }
    return trackAbbr;
  }

  // URL synchronization functions
  function loadFiltersFromURL() {
    if (typeof window === 'undefined') return;

    const params = $page.url.searchParams;

    // Load track (fallback to first available track if not specified)
    const urlTrack = params.get('track');
    if (urlTrack && tracks.includes(urlTrack)) {
      selectedTrack = urlTrack;
    } else if (!selectedTrack && tracks.length > 0) {
      selectedTrack = tracks[0];
    }

    // Load country
    selectedCountry = params.get('country') || '';

    // Load boolean filters
    showPendingValidation = params.get('pending') === 'true';
    showTimesWithoutProof = params.get('unproven') === 'true';
  }

  function updateURL() {
    if (typeof window === 'undefined') return;

    const params = new URLSearchParams();

    // Always include track if selected
    if (selectedTrack) {
      params.set('track', selectedTrack);
    }

    // Include country if selected
    if (selectedCountry) {
      params.set('country', selectedCountry);
    }

    // Include boolean filters if true
    if (showPendingValidation) {
      params.set('pending', 'true');
    }

    if (showTimesWithoutProof) {
      params.set('unproven', 'true');
    }

    // Update URL without triggering navigation
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
  }

  function getProofIcon(proofUrl: string, proofType: string) {
    // Check URL to determine platform
    if (proofUrl.includes('youtube.com') || proofUrl.includes('youtu.be')) {
      return { component: YoutubeSolid, title: 'YouTube Video' };
    } else if (proofUrl.includes('twitch.tv')) {
      return { component: Twitch, title: 'Twitch Video' };
    } else if (proofUrl.includes('twitter.com') || proofUrl.includes('x.com')) {
      return { component: XCompanySolid, title: 'X/Twitter Video' };
    } else if (proofType === 'Screenshot') {
      return { component: CameraFotoSolid, title: 'Screenshot' };
    } else {
      // For both "Video" and "Partial Video" types that don't match specific platforms
      return { component: VideoCameraSolid, title: 'Video' };
    }
  }

  async function markTimeTrialAsInvalid(timeTrialId: string) {
    let conf = window.confirm('Are you sure you would like to mark this time as invalid?');
    if (!conf) return;
    try {
      // Find the time trial record to get its version
      const timeTrialRecord = records.find((record) => record.id === timeTrialId);
      if (!timeTrialRecord) {
        throw new Error('Time trial record not found');
      }

      const response = await fetch(`/api/time-trials/${timeTrialId}/mark-invalid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ version: timeTrialRecord.version }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        if (response.status === 409) {
          throw new Error('This record was modified by another user. Please refresh the page and try again.');
        }
        throw new Error(errorData?.detail || errorData?.title || 'Failed to mark time trial as invalid');
      }

      // Refresh the leaderboard data
      await loadLeaderboard();
    } catch (err) {
      console.error('Error marking time trial as invalid:', err);
      alert(err instanceof Error ? err.message : 'An error occurred while marking the time trial as invalid.');
    }
  }

  onMount(() => {
    // Get tracks from constants based on game
    if (game === 'mkworld') {
      tracks = Object.values(MKWORLD_TRACK_ABBREVIATIONS);
    }
    // Load filters from URL parameters
    loadFiltersFromURL();
    // Initial load
    loadLeaderboard();
  });

  // Watch for filter changes, reload data, and update URL (but don't call during SSR)
  $: if (
    typeof window !== 'undefined' &&
    (selectedTrack ||
      selectedCountry !== undefined ||
      showPendingValidation !== undefined ||
      showTimesWithoutProof !== undefined)
  ) {
    loadLeaderboard();
    updateURL();
  }
</script>

<svelte:head>
  <title
    >{selectedTrack ? getTrackDisplayName(selectedTrack) + ' - ' : ''}{getGameDisplayName(game)}
    {$LL.TIME_TRIALS.LEADERBOARDS()}</title
  >
</svelte:head>

<div class="tracks-container">
  <div class="game-header">
    <div class="flex items-center gap-3">
      <Button href="/{$page.params.lang}/time-trials/{game}" extra_classes="back-button text-white mb-4">
        <ArrowLeftOutline class="w-4 h-4 mr-2" />
        Back to Game homepage
      </Button>
    </div>

    <div class="flex justify-center items-center gap-2 flex-wrap">
      <Button href={`/${$page.params.lang}/time-trials/${game}/timesheet`} size="md" extra_classes="flex items-center">
        🏆 {$LL.TIME_TRIALS.TIMESHEETS()}
      </Button>
      <SubmitButton {game} />
    </div>
  </div>
</div>

<Section header={$LL.TIME_TRIALS.GAME_LEADERBOARDS({ game: getGameDisplayName(game) })}>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="filters rounded-lg border border-gray-700 p-6">
      <div class="space-y-4">
        <!-- First row: Track and Country -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Track Filter -->
          <div>
            <label for="track-select" class="block text-sm font-medium mb-2">
              {$LL.TIME_TRIALS.TRACK_NAME_LABEL()}
            </label>
            <select id="track-select" bind:value={selectedTrack} class="w-full">
              {#each tracks as track, index (index)}
                <option value={track}>{getTrackDisplayName(track)}</option>
              {/each}
            </select>
          </div>

          <!-- Country Filter -->
          <div>
            <label for="country-select" class="block text-sm font-medium mb-2">{$LL.COMMON.COUNTRY()}</label>
            <select id="country-select" bind:value={selectedCountry} class="w-full">
              <option value="">{$LL.COUNTRIES.ALL()}</option>
              {#each countries as country, index (index)}
                <option value={country}>{getCountryDisplayName(country)}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Second row: Validation options -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <!-- Show Pending Validation Checkbox -->
          <div>
            <label class="flex items-center space-x-2 text-sm font-medium">
              <input
                type="checkbox"
                bind:checked={showPendingValidation}
                class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
              />
              <span>{$LL.TIME_TRIALS.SHOW_TIMES.PENDING_VALIDATION()}</span>
            </label>
            <p class="text-xs mt-1">{$LL.TIME_TRIALS.SHOW_TIMES.INCLUDE_AWAITING_VALIDATION()}</p>
          </div>

          <!-- Show Times Without Proof Checkbox -->
          <div>
            <label class="flex items-center space-x-2 text-sm font-medium">
              <input
                type="checkbox"
                bind:checked={showTimesWithoutProof}
                class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
              />
              <span>{$LL.TIME_TRIALS.SHOW_TIMES.PENDING_WITHOUT_PROOF()}</span>
            </label>
            <p class="text-xs mt-1">{$LL.TIME_TRIALS.SHOW_TIMES.INCLUDE_SUBMITTED_WITHOUT_EVIDENCE()}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span class="ml-2 text-gray-400">Loading leaderboard...</span>
      </div>
    {:else if error}
      <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
        <p class="text-red-400">{error}</p>
        <Button extra_classes="mt-2" on:click={loadLeaderboard}>Retry</Button>
      </div>
    {:else if records.length === 0}
      <div class="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <p class="text-gray-400">No records found for this track with the selected filters.</p>
      </div>
    {:else}
      <!-- Leaderboard Table -->
      <div class="rounded-lg border border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-primary-800">
              <tr>
                <th class="px-4 desktop:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  {$LL.TIME_TRIALS.RANK()}
                </th>
                <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider min-w-32">
                  {$LL.TIME_TRIALS.PLAYER()}
                </th>
                <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider"
                  >{$LL.TIME_TRIALS.TIME()}</th
                >
                <th
                  class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden laptop:table-cell"
                >
                  {$LL.TIME_TRIALS.PROOF_EVIDENCE()}
                </th>
                <th
                  class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden desktop:table-cell"
                >
                  {$LL.COMMON.DATE()}
                </th>
                {#if $user && check_permission($user, permissions.validate_time_trial_proof)}
                  <th class="px-4 desktop:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Moderation
                  </th>
                {/if}
              </tr>
            </thead>
            <tbody>
              {#each records as record, index (record.id)}
                <tr class="hover:bg-gray-700">
                  <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                    #{index + 1}
                  </td>
                  <td class="px-4 desktop:px-6 py-4">
                    {#if record.player_name}
                      <a href="/{$page.params.lang}/time-trials/{game}/timesheet?player={record.player_id}">
                        <div class="flex items-center gap-2 flex-wrap">
                          {#if record.player_country_code}
                            <Flag country_code={record.player_country_code} size="small" />
                          {/if}
                          <div class="text-sm max-w-32 text-wrap break-all">
                            {record.player_name}
                          </div>
                        </div>
                      </a>
                    {:else}
                      <span class="font-medium text-white">
                        Player {record.player_id}
                      </span>
                    {/if}
                  </td>

                  <!-- Time Column -->
                  <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm font-mono text-white">
                    {#if record.proofs.length}
                      <a href={record.proofs[0].url}>{formatTime(record.time_ms)}</a>
                    {:else}
                      {formatTime(record.time_ms)}*
                    {/if}
                  </td>
                  <!-- Proof Column -->
                  <td class="px-4 desktop:px-6 py-4 whitespace-nowrap hidden laptop:table-cell">
                    <div class="flex items-center space-x-2">
                      {#if record.proofs && record.proofs.length > 0}
                        <!-- Proof icons -->
                        {#each record.proofs as proof (proof.id)}
                          {@const iconInfo = getProofIcon(proof.url, proof.type)}
                          <a
                            href={proof.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            class="w-5 h-5"
                            title="View proof: {iconInfo.title}"
                          >
                            <svelte:component this={iconInfo.component} />
                            <Popover>
                              <MediaEmbed url={proof.url} fallbackText="Open Proof Link" classes="w-96" />
                            </Popover>
                          </a>
                        {/each}
                        <!-- Status badge (only for non-validated) -->
                        {#if record.validation_status === 'unvalidated'}
                          <span
                            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-900 text-yellow-300"
                          >
                            Pending
                          </span>
                        {/if}
                      {:else}
                        <!-- No proof badge -->
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-700">
                          No Proof
                        </span>
                      {/if}
                    </div>
                  </td>
                  <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm hidden desktop:table-cell">
                    {new Date(record.created_at).toLocaleDateString()}
                  </td>
                  {#if $user && check_permission($user, permissions.validate_time_trial_proof)}
                    <td class="px-4 desktop:px-6 py-4 whitespace-nowrap">
                      <ChevronDownOutline class="inline cursor-pointer" />
                      <Dropdown>
                        <DropdownItem href="/{$page.params.lang}/time-trials/edit?trial_id={record.id}">
                          Edit
                        </DropdownItem>
                        <DropdownItem>
                          <button
                            on:click={() => markTimeTrialAsInvalid(record.id)}
                            class="hover:text-blue-200 text-sm font-medium bg-transparent border-none cursor-pointer"
                          >
                            Mark Invalid
                          </button>
                        </DropdownItem>
                      </Dropdown>
                    </td>
                  {/if}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </div>
</Section>

<style>
  .tracks-container {
    max-width: 1200px;
    margin: 20px auto;
  }

  .game-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
  }

  .filters {
    background-color: rgba(0, 0, 0, 0.2);
  }
  tbody tr {
    background-color: rgba(235, 255, 255, 0.15);
  }
  tbody tr:nth-child(even) {
    background-color: rgba(235, 255, 255, 0.1);
  }
</style>
