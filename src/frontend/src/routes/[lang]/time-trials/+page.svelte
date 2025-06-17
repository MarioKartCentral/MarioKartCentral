<script lang="ts">
    import Section from '$lib/components/common/Section.svelte';
    import Button from '$lib/components/common/buttons/Button.svelte';
    import GameBadge from '$lib/components/badges/GameBadge.svelte';
    import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
    import LL from '$i18n/i18n-svelte';
    import { page } from '$app/stores';
    import { DiscordSolid } from 'flowbite-svelte-icons';
</script>

<svelte:head>
    <title>{$LL.TIME_TRIALS.TITLE()} - MKCentral</title>
    <meta name="description" content="Mario Kart time trials leaderboards and records" />
</svelte:head>

<Section header={$LL.TIME_TRIALS.TITLE()}>
    <div class="space-y-6">
        <div class="flex flex-wrap justify-center desktop:justify-between items-center gap-4">
            <p>
                {$LL.TIME_TRIALS.DESCRIPTION()}
            </p>
            <SubmitButton />
        </div>
        
        <div class="game-container">
            <div class="flex flex-wrap justify-center items-center p-6">
                <div class="flex items-center space-x-3">
                    <GameBadge game="mkworld" />
                    <h3 class="text-lg font-semibold">Mario Kart World</h3>
                </div>
                <div class="p-4 grow grid gap-2">
                    <div>
                        <Button href="/{$page.params.lang}/time-trials/mkworld" color="primary" extra_classes="w-full">
                            {$LL.TIME_TRIALS.VIEW_TRACKS()}
                        </Button>
                    </div>
                    <div>
                        <Button href="/{$page.params.lang}/time-trials/mkworld/leaderboard" color="primary" extra_classes="w-full">
                            {$LL.TIME_TRIALS.LEADERBOARDS()}
                        </Button>
                    </div>
                    <div>
                        <Button href="/{$page.params.lang}/time-trials/mkworld/timesheet" color="primary" extra_classes="w-full">
                            {$LL.TIME_TRIALS.TIMESHEETS()}
                        </Button>
                    </div>
                    <div>
                        <Button href="https://discord.gg/6gDAPxvqh7" color="blue" extra_classes="w-full">
                            <DiscordSolid class="inline mr-2" />
                            {$LL.DISCORD.DISCORD()}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</Section>

<style>
    .game-container {
        background-color: rgba(0, 0, 0, 0.2);
    }
    .grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
</style>
