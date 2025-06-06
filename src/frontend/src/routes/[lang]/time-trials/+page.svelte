<script lang="ts">
    import { GAMES } from '$lib/util/gameConstants';
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import GameBadge from '$lib/components/badges/GameBadge.svelte';
    import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
    import LL from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
</script>

<svelte:head>
    <title>{$LL.TIME_TRIALS.TITLE()} - MKCentral</title>
    <meta name="description" content="Mario Kart time trials leaderboards and records" />
</svelte:head>

<Section header={$LL.TIME_TRIALS.TITLE()}>
    <div class="space-y-6">
        <div class="flex justify-between items-start">
            <p class="text-gray-600 dark:text-gray-300">
                {$LL.TIME_TRIALS.DESCRIPTION()}
            </p>
            
            <SubmitButton />
        </div>
        
        <div class="grid gap-4 md:grid-cols-2">
            {#each Object.entries(GAMES) as [gameId, gameName]}
                <div class="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
                    <div class="flex items-center space-x-3 mb-4">
                        <GameBadge game={gameId} />
                        <h3 class="text-lg font-semibold">{gameName}</h3>
                    </div>
                    
                    <p class="text-gray-600 dark:text-gray-300 mb-4 text-sm">
                        {#if gameId === 'mk8dx'}
                            Browse time trial records for all 96 tracks in Mario Kart 8 Deluxe, including DLC tracks. Filter by engine class (150cc/200cc).
                        {:else if gameId === 'mkworld'}
                            Classic Mario Kart World time trial records for all 12 original tracks.
                        {/if}
                    </p>
                    
                    <Button href="/{$page.params.lang}/time-trials/{gameId}" color="primary" extra_classes="w-full">
                        {$LL.TIME_TRIALS.VIEW_TRACKS()}
                    </Button>
                </div>
            {/each}
        </div>
    </div>
</Section>

<style>
    .grid {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
</style>
