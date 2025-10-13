<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import { GAMES, getTrackFromAbbreviation, MKWORLD_TRACKS, type GameId } from '$lib/util/gameConstants';
  import { formatTimeMs } from '$lib/util/timeTrialUtils';
  import type { TimeTrial, ErrorResponse } from '$lib/types/time-trials';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerInfo } from '$lib/types/player-info';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import {
    XCompanySolid,
    YoutubeSolid,
    CameraFotoSolid,
    VideoCameraSolid,
    ArrowLeftOutline,
  } from 'flowbite-svelte-icons';
  import Twitch from '$lib/components/icons/Twitch.svelte';
  import MediaEmbed from '$lib/components/media/MediaEmbed.svelte';
  import { Popover } from 'flowbite-svelte';
  import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
  import LL from '$i18n/i18n-svelte';

  // URL parameters
  let gameId: GameId;

  // User state
  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  // Data state
  let timeTrials: TimeTrial[] = [];
  let isLoading = true;
  let errorMessage: string | null = null;
  let selectedPlayer: PlayerInfo | null = null;
  let searchPlayer: PlayerInfo | null = null; // For PlayerSearch component
  let searchQuery: string = ' ';

  // Filter state
  let includeUnvalidated = true;
  let includeProofless = true;
  let includeOutdated = false;

  // Helper functions
  function getGameDisplayName(gameId: string): string {
    // gameId should be lowercase (like 'mkworld'), GAMES expects lowercase keys
    return GAMES[gameId as keyof typeof GAMES] || gameId?.toUpperCase() || 'Game';
  }

  function getTrackDisplayName(trackAbbr: string): string {
    if (gameId === 'mkworld') {
      const fullName = getTrackFromAbbreviation(gameId, trackAbbr);
      return fullName || trackAbbr;
    }
    return trackAbbr;
  }

  function getTrackSortOrder(trackAbbr: string): number {
    if (gameId === 'mkworld') {
      const fullName = getTrackFromAbbreviation(gameId, trackAbbr);
      const index = MKWORLD_TRACKS.indexOf(fullName as (typeof MKWORLD_TRACKS)[number]);
      return index >= 0 ? index : 999; // Unknown tracks go to the end
    }
    return 0;
  }

  function sortTimeTrialsByTrackOrder(trials: TimeTrial[]): TimeTrial[] {
    return [...trials].sort((a, b) => {
      const orderA = getTrackSortOrder(a.track);
      const orderB = getTrackSortOrder(b.track);
      return orderA - orderB;
    });
  }

  function getProofIcon(proofUrl: string, proofType: string) {
    if (proofUrl.includes('youtube.com') || proofUrl.includes('youtu.be')) {
      return { component: YoutubeSolid, title: 'YouTube Video' };
    } else if (proofUrl.includes('twitch.tv')) {
      return { component: Twitch, title: 'Twitch Video' };
    } else if (proofUrl.includes('twitter.com') || proofUrl.includes('x.com')) {
      return { component: XCompanySolid, title: 'X/Twitter Video' };
    } else if (proofType === 'Screenshot') {
      return { component: CameraFotoSolid, title: 'Screenshot' };
    } else {
      return { component: VideoCameraSolid, title: 'Video' };
    }
  }

  // Check if current user can edit a specific trial
  function canEditTrial(trial: TimeTrial): boolean {
    if (!user_info) return false;

    // User can edit their own trials
    if (user_info.player?.id?.toString() === trial.player_id.toString()) {
      return true;
    }

    // Staff can edit any trials
    if (check_permission(user_info, permissions.validate_time_trial_proof)) {
      return true;
    }

    return false;
  }

  onMount(async () => {
    gameId = $page.params.game as GameId;

    // Get player from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const urlPlayerId = urlParams.get('player');

    if (urlPlayerId !== null) {
      const urlPlayerIdAsNumber = Number(urlPlayerId);

      let isValidPlayerId = !isNaN(urlPlayerIdAsNumber);
      if (isValidPlayerId) {
        const playerResponse = await fetch(`/api/registry/players/${urlPlayerIdAsNumber}`);
        isValidPlayerId = playerResponse.status === 200;
        if (isValidPlayerId) {
          const playerData = await playerResponse.json();
          updatePlayer(playerData);
        }
      }

      if (!isValidPlayerId) {
        updatePlayer(null);
      }
    } else {
      updatePlayer(user_info?.player);
    }
  });

  async function fetchTimesheet() {
    // Get playerId from selectedPlayer if available, otherwise from URL
    const currentPlayerId = selectedPlayer === null ? null : selectedPlayer.id;

    if (!currentPlayerId || (!selectedPlayer && timeTrials.length)) {
      timeTrials = [];
      isLoading = false;
      return;
    }

    try {
      isLoading = true;
      errorMessage = null;

      const params = new URLSearchParams({
        player_id: currentPlayerId.toString(),
        game: gameId,
        include_unvalidated: includeUnvalidated.toString(),
        include_proofless: includeProofless.toString(),
        include_outdated: includeOutdated.toString(),
      });

      const response = await fetch(`/api/time-trials/timesheet?${params}`);

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        errorMessage = errorData.detail || 'Failed to load timesheet';
        return;
      }

      const data = await response.json();
      let records = data.records || [];

      // Sort by track order
      records = sortTimeTrialsByTrackOrder(records);
      timeTrials = records;
    } catch (error) {
      console.error('Error fetching timesheet:', error);
      errorMessage = 'Network error. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  // Reactive statement to refetch when any relevant data changes
  $: if (gameId && selectedPlayer !== null) {
    // Touch filter variables to make them reactive dependencies
    (includeUnvalidated, includeProofless, includeOutdated);
    fetchTimesheet();
  }

  function updatePlayer(player: PlayerInfo | null) {
    selectedPlayer = player;
    searchPlayer = null;
    searchQuery = player?.name ?? '';

    if (typeof window !== 'undefined') {
      const newUrl = new URL(window.location.href);
      if (player === null) {
        newUrl.searchParams.delete('player');
      } else {
        newUrl.searchParams.set('player', player.id.toString());
      }
      window.history.replaceState({}, '', newUrl.toString());
    }

    fetchTimesheet();
  }

  // Watch for user login/logout changes
  $: if (user_info && selectedPlayer === null && user_info.player !== null) {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('player') === null) {
      updatePlayer(user_info.player);
    }
  }

  // Update page when new player is selected
  $: if (searchPlayer !== null) {
    if (searchPlayer.id !== selectedPlayer?.id) {
      updatePlayer(searchPlayer);
    }

    searchPlayer = null;
  }
</script>

<div class="tracks-container">
  <div class="game-header">
    <div class="flex items-center gap-3">
      <Button href="/{$page.params.lang}/time-trials/{gameId}" extra_classes="back-button text-white mb-4">
        <ArrowLeftOutline class="w-4 h-4 mr-2" />
        Back to Game homepage
      </Button>
    </div>

    <div class="flex justify-center items-center gap-2 flex-wrap">
      <Button
        href={`/${$page.params.lang}/time-trials/${gameId}/leaderboard`}
        size="md"
        extra_classes="flex items-center"
      >
        🏆 {$LL.TIME_TRIALS.LEADERBOARDS()}
      </Button>
      <SubmitButton game={gameId} />
    </div>
  </div>

  <Section header="{selectedPlayer ? `${selectedPlayer.name}'s ` : ''}{getGameDisplayName(gameId)} Timesheet">
    <div slot="header_content">
      <div class="flex items-center gap-3">
        {#if selectedPlayer}
          {#if selectedPlayer?.country_code}
            <Flag country_code={selectedPlayer?.country_code} />
          {/if}
          <a
            href="/{$page.params.lang}/registry/players/profile?id={selectedPlayer.id}"
            class="text-primary hover:underline"
          >
            View Profile
          </a>
        {/if}
      </div>
    </div>

    <div class="space-y-6">
      <!-- Filters -->
      <div class="filters rounded-lg border border-gray-700 p-6">
        <div class="space-y-4">
          <!-- First row: Player Search -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="player-search" class="block text-sm font-medium mb-2"> Player </label>
              <PlayerSearch bind:player={searchPlayer} show_add_button={false} bind:query={searchQuery} />
              <p class="text-sm text-gray-400 mt-1">Search for a player to view their timesheet</p>
            </div>
          </div>

          <!-- Second row: Validation options -->
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <!-- Show Pending Validation Checkbox -->
            <div>
              <label class="flex items-center space-x-2 text-sm font-medium">
                <input
                  type="checkbox"
                  bind:checked={includeUnvalidated}
                  class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span>Show times pending validation</span>
              </label>
              <p class="text-xs mt-1">Include times awaiting validation review</p>
            </div>

            <!-- Show Times Without Proof Checkbox -->
            <div>
              <label class="flex items-center space-x-2 text-sm font-medium">
                <input
                  type="checkbox"
                  bind:checked={includeProofless}
                  class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span>Show times without proof</span>
              </label>
              <p class="text-xs mt-1">Include times submitted without evidence</p>
            </div>

            <!-- Show Outdated Times Checkbox -->
            <div>
              <label class="flex items-center space-x-2 text-sm font-medium">
                <input
                  type="checkbox"
                  bind:checked={includeOutdated}
                  class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span>Show outdated times</span>
              </label>
              <p class="text-xs mt-1">Include older submissions that have been beaten</p>
            </div>
          </div>
        </div>
      </div>

      {#key timeTrials}
        {#if !selectedPlayer}
          <div class="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <p class="text-gray-400">Search for a player above to view their timesheet.</p>
          </div>
        {:else if isLoading}
          <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span class="ml-2 text-gray-400">Loading timesheet...</span>
          </div>
        {:else if errorMessage}
          <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
            <p class="text-red-400">{errorMessage}</p>
            <Button extra_classes="mt-2" on:click={fetchTimesheet}>Retry</Button>
          </div>
        {:else if timeTrials.length === 0}
          <div class="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <p class="text-gray-400">
              No records found for {selectedPlayer.name} with the selected filters.
            </p>
          </div>
        {:else}
          <!-- Timesheet Table -->
          <div class="rounded-lg border border-gray-700 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-primary-800">
                  <tr>
                    <th class="px-4 desktop:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Track
                    </th>
                    <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider"> Time </th>
                    <th
                      class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden laptop:table-cell"
                    >
                      Proof
                    </th>
                    <th
                      class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden desktop:table-cell"
                    >
                      Date
                    </th>
                    {#if timeTrials.some((record) => canEditTrial(record))}
                      <th class="px-4 desktop:px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                        Edit
                      </th>
                    {/if}
                  </tr>
                </thead>
                <tbody>
                  {#each timeTrials as trial}
                    <tr class="hover:bg-gray-700">
                      <!-- Track Column -->
                      <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                        {getTrackDisplayName(trial.track)}
                      </td>

                      <!-- Time Column -->
                      <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm font-mono text-white">
                        {#if trial.proofs.length}
                          <a href={trial.proofs[0].url}>{formatTimeMs(trial.time_ms)}</a>
                        {:else}
                          {formatTimeMs(trial.time_ms)}*
                        {/if}
                      </td>

                      <!-- Proof Column -->
                      <td class="px-4 desktop:px-6 py-4 whitespace-nowrap hidden laptop:table-cell">
                        <div class="flex items-center space-x-2">
                          {#if trial.proofs && trial.proofs.length > 0}
                            <!-- Proof icons -->
                            {#each trial.proofs as proof}
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
                            {#if trial.validation_status === 'unvalidated'}
                              <span
                                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-900 text-yellow-300"
                              >
                                Pending
                              </span>
                            {/if}
                          {:else}
                            <!-- No proof badge -->
                            <span
                              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-700"
                            >
                              No Proof
                            </span>
                          {/if}
                        </div>
                      </td>

                      <!-- Date Column -->
                      <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm hidden desktop:table-cell">
                        {new Date(trial.created_at).toLocaleDateString()}
                      </td>

                      <!-- Edit Column -->
                      {#if timeTrials.some((r) => canEditTrial(r))}
                        <td class="px-4 desktop:px-6 py-4 whitespace-nowrap">
                          {#if canEditTrial(trial)}
                            <a
                              href="/{$page.params.lang}/time-trials/edit?trial_id={trial.id}"
                              class="text-blue-400 hover:text-blue-200 text-sm font-medium"
                            >
                              Edit
                            </a>
                          {/if}
                        </td>
                      {/if}
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        {/if}
      {/key}
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
