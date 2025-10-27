/**
 * Game and track constants for time trials
 */

export const GAMES = {
  mkworld: 'Mario Kart World',
} as const;

export type GameId = keyof typeof GAMES;

// MK8DX removed

// MK8DX abbreviations removed

// MK8DX reverse mapping removed

export const MKWORLD_TRACKS = [
  'Mario Bros. Circuit',
  'Crown City',
  'Whistlestop Summit',
  'DK Spaceport',
  'Desert Hills',
  'Shy Guy Bazaar',
  'Wario Stadium',
  'Airship Fortress',
  'DK Pass',
  'Starview Peak',
  'Sky High Sundae',
  'Wario Shipyard',
  'Koopa Troopa Beach',
  'Faraway Oasis',
  'Peach Stadium',
  'Peach Beach',
  'Salty Salty Speedway',
  'Dino Dino Jungle',
  'Great ? Block Ruins',
  'Cheep Cheep Falls',
  'Dandelion Depths',
  'Boo Cinema',
  'Dry Bones Burnout',
  'Moo Moo Meadows',
  'Choco Mountain',
  "Toad's Factory",
  "Bowser's Castle",
  'Acorn Heights',
  'Mario Circuit',
  'Rainbow Road',
] as const;

// Simple abbreviations for MKWorld tracks (updated)
export const MKWORLD_TRACK_ABBREVIATIONS: Record<string, string> = {
  'Mario Bros. Circuit': 'MBC',
  'Crown City': 'CC',
  'Whistlestop Summit': 'WS',
  'DK Spaceport': 'DKS',
  'Desert Hills': 'rDH',
  'Shy Guy Bazaar': 'rSGB',
  'Wario Stadium': 'rWS',
  'Airship Fortress': 'rAF',
  'DK Pass': 'rDKP',
  'Starview Peak': 'SP',
  'Sky High Sundae': 'rSHS',
  'Wario Shipyard': 'rWSh',
  'Koopa Troopa Beach': 'rKTB',
  'Faraway Oasis': 'FO',
  'Peach Stadium': 'PS',
  'Peach Beach': 'rPB',
  'Salty Salty Speedway': 'SSS',
  'Dino Dino Jungle': 'rDDJ',
  'Great ? Block Ruins': 'GBR',
  'Cheep Cheep Falls': 'CCF',
  'Dandelion Depths': 'DD',
  'Boo Cinema': 'BCi',
  'Dry Bones Burnout': 'DBB',
  'Moo Moo Meadows': 'rMMM',
  'Choco Mountain': 'rCM',
  "Toad's Factory": 'rTF',
  "Bowser's Castle": 'BC',
  'Acorn Heights': 'AH',
  'Mario Circuit': 'rMC',
  'Rainbow Road': 'RR',
};

// Track names for internationalization with i18n types
export const MKWORLD_TRACK_TRANSLATION_IDS: Record<string, string> = {
  'Mario Bros. Circuit': 'MARIO_BROS_CIRCUIT',
  'Crown City': 'CROWN_CITY',
  'Whistlestop Summit': 'WHISTLESTOP_SUMMIT',
  'DK Spaceport': 'DK_SPACEPORT',
  'Desert Hills': 'DESERT_HILLS',
  'Shy Guy Bazaar': 'SHY_GUY_BAZAAR',
  'Wario Stadium': 'WARIO_STADIUM',
  'Airship Fortress': 'AIRSHIP_FORTRESS',
  'DK Pass': 'DK_PASS',
  'Starview Peak': 'STARVIEW_PEAK',
  'Sky High Sundae': 'SKY_HIGH_SUNDAE',
  'Wario Shipyard': 'WARIO_SHIPYARD',
  'Koopa Troopa Beach': 'KOOPA_TROOPA_BEACH',
  'Faraway Oasis': 'FARAWAY_OASIS',
  'Peach Stadium': 'PEACH_STADIUM',
  'Peach Beach': 'PEACH_BEACH',
  'Salty Salty Speedway': 'SALTY_SALTY_SPEEDWAY',
  'Dino Dino Jungle': 'DINO_DINO_JUNGLE',
  'Great ? Block Ruins': 'GREAT_BLOCK_RUINS',
  'Cheep Cheep Falls': 'CHEEP_CHEEP_FALLS',
  'Dandelion Depths': 'DANDELION_DEPTHS',
  'Boo Cinema': 'BOO_CINEMA',
  'Dry Bones Burnout': 'DRY_BONES_BURNOUT',
  'Moo Moo Meadows': 'MOO_MOO_MEADOWS',
  'Choco Mountain': 'CHOCO_MOUNTAIN',
  "Toad's Factory": 'TOADS_FACTORY',
  "Bowser's Castle": 'BOWSERS_CASTLE',
  'Acorn Heights': 'ACORN_HEIGHTS',
  'Mario Circuit': 'MARIO_CIRCUIT',
  'Rainbow Road': 'RAINBOW_ROAD',
};

// Reverse mapping for MKWorld
export const MKWORLD_ABBREVIATION_TO_TRACK = Object.fromEntries(
  Object.entries(MKWORLD_TRACK_ABBREVIATIONS).map(([track, abbr]) => [abbr, track]),
);

export const TRACKS_BY_GAME = {
  mkworld: MKWORLD_TRACKS,
} as const;

export const TRACK_ABBREVIATIONS_BY_GAME = {
  mkworld: MKWORLD_TRACK_ABBREVIATIONS,
} as const;

export const ABBREVIATION_TO_TRACK_BY_GAME = {
  mkworld: MKWORLD_ABBREVIATION_TO_TRACK,
} as const;

export const ENGINE_CLASSES = {
  mkworld: [150], // Only 150cc for Mario Kart World
} as const;

// Helper functions for track name/abbreviation conversion
export function getTrackAbbreviation(game: GameId, trackName: string): string {
  return TRACK_ABBREVIATIONS_BY_GAME[game][trackName] || trackName;
}

export function getTrackFromAbbreviation(game: GameId, abbreviation: string): string {
  return ABBREVIATION_TO_TRACK_BY_GAME[game][abbreviation] || abbreviation;
}
