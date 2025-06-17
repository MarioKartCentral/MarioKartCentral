<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { user } from '$lib/stores/stores';
    import { check_permission, permissions } from '$lib/util/permissions';
    import { 
        GAMES, 
        getTrackFromAbbreviation,
        MKWORLD_TRACKS,
        type GameId 
    } from '$lib/util/gameConstants';
    import { formatTimeMs } from '$lib/util/timeTrialUtils';
    import type { TimeTrial, ErrorResponse } from '$lib/types/time-trials';
    import type { UserInfo } from '$lib/types/user-info';
    import type { PlayerInfo } from '$lib/types/player-info';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import Flag from '$lib/components/common/Flag.svelte';
    import Section from '$lib/components/common/Section.svelte';
    import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
    import { XCompanySolid, YoutubeSolid, CameraFotoSolid, VideoCameraSolid, ArrowLeftOutline } from 'flowbite-svelte-icons';
    import Twitch from '$lib/components/icons/Twitch.svelte';
    import MediaEmbed from '$lib/components/media/MediaEmbed.svelte';
    import { Popover } from 'flowbite-svelte';

    // URL parameters
    let gameId: GameId;
    let playerId: string | null = null;
    
    // User state
    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    // Data state
    let timeTrials: TimeTrial[] = [];
    let isLoading = true;
    let errorMessage: string | null = null;
    let selectedPlayer: PlayerInfo | null = null; // Will be used with PlayerSearch
    let playerName: string = '';
    let playerCountryCode: string | null = null;

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
            const index = MKWORLD_TRACKS.indexOf(fullName as typeof MKWORLD_TRACKS[number]);
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

    onMount(async() => {
        gameId = $page.params.game as GameId;
        
        // Get player_id from URL params
        const urlParams = new URLSearchParams(window.location.search);
        const urlPlayerId = urlParams.get('player_id');
        
        if (urlPlayerId) {
            // Use the player ID from URL
            playerId = urlPlayerId;
            const playerResponse = await fetch(`/api/registry/players/${playerId}`);
            if(playerResponse.status === 200) {
                selectedPlayer = await playerResponse.json();
            }
        } else if (user_info?.player?.id) {
            // No URL player_id, use logged-in player
            playerId = user_info.player.id.toString();
            selectedPlayer = user_info.player;
            
            // Update URL to include the player_id for sharing/bookmarking
            if (typeof window !== 'undefined') {
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('player_id', playerId);
                window.history.replaceState({}, '', newUrl.toString());
            }
        }

        fetchTimesheet();
    });

    async function fetchTimesheet() {
        // Get playerId from selectedPlayer if available, otherwise from URL
        const currentPlayerId = selectedPlayer?.id?.toString() || playerId;
        
        if (!currentPlayerId || (!selectedPlayer && timeTrials.length)) {
            timeTrials = [];
            playerName = '';
            playerCountryCode = null;
            isLoading = false;
            return;
        }
        
        try {
            isLoading = true;
            errorMessage = null;

            const params = new URLSearchParams({
                player_id: currentPlayerId,
                game: gameId,
                include_unvalidated: includeUnvalidated.toString(),
                include_proofless: includeProofless.toString(),
                include_outdated: includeOutdated.toString()
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
            
            // Extract player info from first record or selectedPlayer
            if (records.length > 0) {
                playerName = records[0].player_name || selectedPlayer?.name || null;
                playerCountryCode = records[0].player_country_code || selectedPlayer?.country_code || null;
            } else if (selectedPlayer) {
                playerName = selectedPlayer.name;
                playerCountryCode = selectedPlayer.country_code || null;
            } else {
                playerName = `Player ${currentPlayerId}`;
                playerCountryCode = null;
            }

        } catch (error) {
            console.error('Error fetching timesheet:', error);
            errorMessage = 'Network error. Please try again.';
        } finally {
            isLoading = false;
        }
    }

    // Reactive statement to refetch when any relevant data changes
    $: if (gameId && (selectedPlayer || playerId)) {
        // Touch filter variables to make them reactive dependencies
        includeUnvalidated, includeProofless, includeOutdated;
        fetchTimesheet();
    }
    
    // Watch for user login/logout changes
    $: if (user_info && !playerId && user_info.player?.id) {
        // User logged in and no player was previously selected, use their player
        playerId = user_info.player.id.toString();
        selectedPlayer = user_info.player;
        
        // Update URL
        if (typeof window !== 'undefined') {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('player_id', playerId);
            window.history.replaceState({}, '', newUrl.toString());
        }
    }
    
    // Navigate to new page when player is selected
    $: if (selectedPlayer && selectedPlayer.id.toString() !== playerId) {
        const newUrl = `/${$page.params.lang}/time-trials/${gameId}/timesheet?player_id=${selectedPlayer.id}`;
        goto(newUrl);
    }
</script>

<svelte:head>
    <title>{playerName ? `${playerName}'s Timesheet` : 'Timesheet'} - {getGameDisplayName(gameId)}</title>
</svelte:head>

<div class="tracks-container">
    <Button href="/{$page.params.lang}/time-trials/{gameId}" extra_classes="back-button text-white mb-4">
        <ArrowLeftOutline class="w-4 h-4 mr-2" />
        Back to Game homepage
    </Button>
</div>

<Section header="{playerName ? `${playerName}'s ` : ''}{getGameDisplayName(gameId)} Timesheet">
    <div slot="header_content">
        <div class="flex items-center gap-3">
            {#if selectedPlayer}
                {#if playerCountryCode}
                    <Flag country_code={playerCountryCode} />
                {/if}
                <a 
                    href="/{$page.params.lang}/registry/players/profile?id={selectedPlayer?.id || playerId}" 
                    class="text-primary hover:underline"
                >
                    View Profile
                </a>
            {/if}
            
        </div>
    </div>

    <!-- Filters -->
    <div class="filters rounded-lg border border-gray-700 p-6">
        <div class="space-y-4">
            <!-- First row: Player Search -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label for="player-search" class="block text-sm font-medium mb-2">
                        Player
                    </label>
                    <PlayerSearch bind:player={selectedPlayer} />
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
                    <p class="text-xs mt-1">
                        Include times awaiting validation review
                    </p>
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
                    <p class="text-xs mt-1">
                        Include times submitted without evidence
                    </p>
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
                    <p class="text-xs mt-1">
                        Include older submissions that have been beaten
                    </p>
                </div>
            </div>
        </div>
    </div>

    {#key timeTrials}
        {#if isLoading}
            <div class="flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span class="ml-2 text-gray-400">Loading timesheet...</span>
            </div>
        {:else if errorMessage}
            <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
                <p class="text-red-400">{errorMessage}</p>
                <Button extra_classes="mt-2" on:click={fetchTimesheet}>Retry</Button>
            </div>
        {:else if !selectedPlayer}
            <div class="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
                <p class="text-gray-400">
                    Search for a player above to view their timesheet.
                </p>
            </div>
        {:else if timeTrials.length === 0}
            <div class="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
                <p class="text-gray-400">
                    No records found for {playerName} with the selected filters.
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
                                <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider">
                                    Time
                                </th>
                                <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden desktop:table-cell">
                                    Proof
                                </th>
                                <th class="px-4 desktop:px-6 text-left text-xs font-medium uppercase tracking-wider hidden desktop:table-cell">
                                    Date
                                </th>
                                {#if timeTrials.some(record => canEditTrial(record))}
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
                                    <td class="px-4 desktop:px-6 py-4 whitespace-nowrap hidden desktop:table-cell">
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
                                                        <svelte:component this={iconInfo.component}/>
                                                        <Popover>
                                                            <MediaEmbed url={proof.url} 
                                                            fallbackText="Open Proof Link"
                                                            classes="w-96"/>
                                                        </Popover>
                                                    </a>
                                                {/each}
                                                <!-- Status badge (only for non-validated) -->
                                                {#if trial.validation_status === 'unvalidated'}
                                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-900 text-yellow-300">
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
                                    
                                    <!-- Date Column -->
                                    <td class="px-4 desktop:px-6 py-4 whitespace-nowrap text-sm hidden desktop:table-cell">
                                        {new Date(trial.created_at).toLocaleDateString()}
                                    </td>
                                    
                                    <!-- Edit Column -->
                                    {#if timeTrials.some(r => canEditTrial(r))}
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

            <!-- Summary -->
            <div class="mt-6 p-4 bg-gray-800 rounded border border-gray-600">
                <div class="text-sm text-gray-300">
                    Showing {timeTrials.length} time trial{timeTrials.length !== 1 ? 's' : ''} for {playerName}
                    {#if !includeOutdated}
                        <span class="text-gray-500">(best times only - enable "Show outdated times" to see all submissions)</span>
                    {/if}
                </div>
            </div>
        {/if}
    {/key}
    
</Section>

<style>
    .tracks-container {
        max-width: 1200px;
        margin: 20px auto;
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
