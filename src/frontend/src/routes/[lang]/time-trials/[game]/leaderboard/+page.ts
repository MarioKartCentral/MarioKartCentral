import type { PageLoad } from './$types';
import { MKWORLD_TRACK_ABBREVIATIONS } from '$lib/util/gameConstants';

export const load: PageLoad = async ({ params }) => {
  const game = params.game;

  // Get track data based on the game
  let tracks = {};
  if (game === 'mkworld') {
    // Convert track abbreviations to track data format
    // This gives us ALL tracks from the constants, not just ones with records
    tracks = Object.fromEntries(
      Object.entries(MKWORLD_TRACK_ABBREVIATIONS).map(([fullName, abbr]) => [abbr, { name: fullName }]),
    );
  }

  return {
    game,
    gameData: {
      tracks,
    },
  };
};
