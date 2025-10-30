<script lang="ts">
  import { page } from '$app/stores';
  import {
    GAMES,
    TRACKS_BY_GAME,
    MKWORLD_TRACK_TRANSLATION_IDS,
    getTrackAbbreviation,
    type GameId,
  } from '$lib/util/gameConstants';
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import SubmitButton from '$lib/components/time-trials/SubmitButton.svelte';
  import { ArrowLeftOutline, BadgeCheckOutline } from 'flowbite-svelte-icons';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  $: game = $page.params.game as GameId;
  $: tracks = TRACKS_BY_GAME[game] || [];
  $: gameName = GAMES[game] || 'Unknown Game';

  function getTranslatedTrackName(game: GameId, track: string): string {
    if (GAMES[game] === GAMES.mkworld) {
      const trackId = MKWORLD_TRACK_TRANSLATION_IDS[track as keyof typeof MKWORLD_TRACK_TRANSLATION_IDS];
      return $LL.MARIO_KART_WORLD.TRACKS[trackId as keyof typeof $LL.MARIO_KART_WORLD.TRACKS]();
    }
    return track;
  }
</script>

<div class="tracks-container">
  <Button href={`/${$page.params.lang}/time-trials`} extra_classes="back-button text-white mb-4">
    <ArrowLeftOutline class="w-4 h-4 mr-2" />
    Back to All Games
  </Button>

  <div class="game-header">
    <div class="flex items-center gap-3">
      <h1 class="text-white">{gameName} Time Trials</h1>
    </div>

    <div class="flex justify-center items-center gap-2 flex-wrap">
      <Button
        href={`/${$page.params.lang}/time-trials/${game}/leaderboard`}
        size="md"
        extra_classes="flex items-center"
      >
        🏆 {$LL.TIME_TRIALS.LEADERBOARDS()}
      </Button>
      <Button href={`/${$page.params.lang}/time-trials/${game}/timesheet`} size="md" extra_classes="flex items-center">
        📝 {$LL.TIME_TRIALS.TIMESHEETS()}
      </Button>
      <SubmitButton {game} />
      {#if $user && check_permission($user, permissions.validate_time_trial_proof)}
        <Button
          href={`/${$page.params.lang}/time-trials/${game}/validation`}
          color="blue"
          size="md"
          extra_classes="flex items-center"
        >
          <BadgeCheckOutline class="w-5 h-5 mr-2" />
          {$LL.TIME_TRIALS.VALIDATE_PROOFS_BUTTON()}
        </Button>
      {/if}
    </div>
  </div>

  <Section header="Select a Track">
    <div class="tracks-grid">
      {#each tracks as track}
        <Button
          color="primary"
          size="lg"
          extra_classes="flex items-center"
          href={`/${$page.params.lang}/time-trials/${game}/leaderboard?track=${getTrackAbbreviation(game, track)}`}
        >
          {getTranslatedTrackName(game, track) || track}
        </Button>
      {/each}
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

  .game-header h1 {
    font-size: 2rem;
    font-weight: bold;
    margin: 0;
  }

  .tracks-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 16px;
  }

  @media (max-width: 1024px) {
    .tracks-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 768px) {
    .tracks-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 480px) {
    .tracks-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
