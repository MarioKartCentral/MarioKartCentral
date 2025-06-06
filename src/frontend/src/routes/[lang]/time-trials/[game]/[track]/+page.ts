import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import { getTrackFromAbbreviation, TRACKS_BY_GAME, type GameId } from '$lib/util/gameConstants';

export const load: PageLoad = async ({ params, url }) => {
    const { game, track: trackAbbr } = params;
    
    // Validate game
    if (!(game in TRACKS_BY_GAME)) {
        throw error(404, `Game '${game}' not found`);
    }
    
    const gameId = game as GameId;
    
    // Convert abbreviation to full track name
    const trackName = getTrackFromAbbreviation(gameId, trackAbbr);
    
    // If conversion failed (returns original abbreviation), track doesn't exist
    if (trackName === trackAbbr) {
        throw error(404, `Track abbreviation '${trackAbbr}' not found for game '${game}'`);
    }
    
    // Validate track exists for this game
    const tracksForGame = TRACKS_BY_GAME[gameId];
    if (!(tracksForGame as readonly string[]).includes(trackName)) {
        throw error(404, `Track '${trackName}' not found for game '${game}'`);
    }
    
    const cc = url.searchParams.get('cc');
    
    return {
        game: gameId,
        track: trackName,
        trackAbbr: trackAbbr,
        cc: cc ? parseInt(cc) : null
    };
};
