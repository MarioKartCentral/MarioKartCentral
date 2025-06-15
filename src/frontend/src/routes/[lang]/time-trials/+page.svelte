<script lang="ts">
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
            <p class="text-gray-300">
                {$LL.TIME_TRIALS.DESCRIPTION()}
            </p>
            
            <SubmitButton />
        </div>
        
        <div class="grid gap-4 md:grid-cols-2">
            <div class="p-6 bg-gray-800 rounded-lg border border-gray-700 hover:shadow-md transition-shadow">
                <div class="flex items-center space-x-3 mb-4">
                    <GameBadge game="mkworld" />
                    <h3 class="text-lg font-semibold text-white">Mario Kart World</h3>
                </div>
                
                <div class="space-y-3">
                    <Button href="/{$page.params.lang}/time-trials/mkworld" color="primary" extra_classes="w-full">
                        {$LL.TIME_TRIALS.VIEW_TRACKS()}
                    </Button>
                    
                    <Button href="/{$page.params.lang}/time-trials/mkworld/leaderboard" color="blue" extra_classes="w-full">
                        {$LL.TIME_TRIALS.LEADERBOARDS()}
                    </Button>
                </div>
            </div>
        </div>
    </div>
</Section>

<style>
    .grid {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
</style>
