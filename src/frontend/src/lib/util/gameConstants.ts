/**
 * Game and track constants for time trials
 */

export const GAMES = {
    mk8dx: 'Mario Kart 8 Deluxe',
    mkworld: 'Mario Kart World'
} as const;

export type GameId = keyof typeof GAMES;

export const MK8DX_TRACKS = [
    // Mushroom Cup
    'Mario Kart Stadium',
    'Water Park', 
    'Sweet Sweet Canyon',
    'Thwomp Ruins',
    
    // Flower Cup
    'Mario Circuit',
    'Toad Harbor',
    'Twisted Mansion',
    'Shy Guy Falls',
    
    // Star Cup
    'Sunshine Airport',
    'Dolphin Shoals',
    'Electrodrome',
    'Mount Wario',
    
    // Special Cup
    'Cloudtop Cruise',
    'Bone-Dry Dunes',
    'Bowser\'s Castle',
    'Rainbow Road',
    
    // Shell Cup (Retro)
    'Moo Moo Meadows',
    'Mario Circuit (GBA)',
    'Cheep Cheep Beach',
    'Toad\'s Turnpike',
    
    // Banana Cup (Retro)
    'Dry Dry Desert',
    'Donut Plains 3',
    'Royal Raceway',
    'DK Jungle',
    
    // Leaf Cup (Retro)
    'Wario Stadium',
    'Sherbet Land',
    'Music Park',
    'Yoshi Valley',
    
    // Lightning Cup (Retro)
    'Tick-Tock Clock',
    'Piranha Plant Slide',
    'Grumble Volcano',
    'Rainbow Road (N64)',
    
    // Egg Cup (DLC 1)
    'Yoshi Circuit',
    'Excitebike Arena',
    'Dragon Driftway',
    'Mute City',
    
    // Triforce Cup (DLC 1)
    'Wario\'s Gold Mine',
    'Rainbow Road (SNES)',
    'Ice Ice Outpost',
    'Hyrule Circuit',
    
    // Crossing Cup (DLC 2)
    'Baby Park',
    'Cheese Land',
    'Wild Woods',
    'Animal Crossing',
    
    // Bell Cup (DLC 2)
    'Neo Bowser City',
    'Ribbon Road',
    'Super Bell Subway',
    'Big Blue',
    
    // Golden Dash Cup (DLC 3)
    'Paris Promenade',
    'Toad Circuit',
    'Choco Mountain',
    'Coconut Mall',
    
    // Lucky Cat Cup (DLC 3)
    'Tokyo Blur',
    'Shroom Ridge',
    'Sky Garden',
    'Ninja Hideaway',
    
    // Turnip Cup (DLC 3)
    'New York Minute',
    'Mario Circuit 3',
    'Kalimari Desert',
    'Waluigi Pinball',
    
    // Propeller Cup (DLC 3)
    'Sydney Sprint',
    'Snow Land',
    'Mushroom Gorge',
    'Sky-High Sundae',
    
    // Rock Cup (DLC 4)
    'London Loop',
    'Boo Lake',
    'Rock Rock Mountain',
    'Maple Treeway',
    
    // Moon Cup (DLC 4)
    'Berlin Byways',
    'Peach Gardens',
    'Merry Mountain',
    'Rainbow Road (3DS)',
    
    // Fruit Cup (DLC 4)
    'Amsterdam Drift',
    'Riverside Park',
    'DK Summit',
    'Yoshi\'s Island',
    
    // Boomerang Cup (DLC 4)
    'Bangkok Rush',
    'Mario Circuit (DS)',
    'Waluigi Stadium',
    'Singapore Speedway',
    
    // Feather Cup (DLC 5)
    'Athens Dash',
    'Daisy Cruiser',
    'Moonview Highway',
    'Squeaky Clean Sprint',
    
    // Cherry Cup (DLC 5)
    'Los Angeles Laps',
    'Sunset Wilds',
    'Koopa Cape',
    'Vancouver Velocity',
    
    // Acorn Cup (DLC 5)
    'Rome Avanti',
    'DK Mountain',
    'Daisy Circuit',
    'Piranha Plant Cove',
    
    // Spiny Cup (DLC 5)
    'Madrid Drive',
    'Rosalina\'s Ice World',
    'Bowser\'s Castle 3',
    'Rainbow Road (Wii)'
] as const;

// Track abbreviations for MK8DX (for cleaner URLs)
export const MK8DX_TRACK_ABBREVIATIONS: Record<string, string> = {
    // Mushroom Cup
    'Mario Kart Stadium': 'MKS',
    'Water Park': 'WP',
    'Sweet Sweet Canyon': 'SSC',
    'Thwomp Ruins': 'TR',
    
    // Flower Cup
    'Mario Circuit': 'MC',
    'Toad Harbor': 'TH',
    'Twisted Mansion': 'TM',
    'Shy Guy Falls': 'SGF',
    
    // Star Cup
    'Sunshine Airport': 'SA',
    'Dolphin Shoals': 'DS',
    'Electrodrome': 'Ed',
    'Mount Wario': 'MW',
    
    // Special Cup
    'Cloudtop Cruise': 'CC',
    'Bone-Dry Dunes': 'BDD',
    'Bowser\'s Castle': 'BC',
    'Rainbow Road': 'RR',
    
    // Shell Cup (Retro)
    'Moo Moo Meadows': 'rMMM',
    'Mario Circuit (GBA)': 'rMC',
    'Cheep Cheep Beach': 'rCCB',
    'Toad\'s Turnpike': 'rTT',
    
    // Banana Cup (Retro)
    'Dry Dry Desert': 'rDDD',
    'Donut Plains 3': 'rDP3',
    'Royal Raceway': 'rRRy',
    'DK Jungle': 'rDKJ',
    
    // Leaf Cup (Retro)
    'Wario Stadium': 'rWS',
    'Sherbet Land': 'rSL',
    'Music Park': 'rMP',
    'Yoshi Valley': 'rYV',
    
    // Lightning Cup (Retro)
    'Tick-Tock Clock': 'rTTC',
    'Piranha Plant Slide': 'rPPS',
    'Grumble Volcano': 'rGV',
    'Rainbow Road (N64)': 'rRRd',
    
    // Egg Cup (DLC Wave 1)
    'Yoshi Circuit': 'dYC',
    'Excitebike Arena': 'dEA',
    'Dragon Driftway': 'dDD',
    'Mute City': 'dMC',
    
    // Triforce Cup (DLC Wave 1)
    'Wario\'s Gold Mine': 'dWGM',
    'Rainbow Road (SNES)': 'dRR',
    'Ice Ice Outpost': 'dIIO',
    'Hyrule Circuit': 'dHC',
    
    // Crossing Cup (DLC Wave 2)
    'Baby Park': 'dBP',
    'Cheese Land': 'dCL',
    'Wild Woods': 'dWW',
    'Animal Crossing': 'dAC',
    
    // Bell Cup (DLC Wave 2)
    'Neo Bowser City': 'dNBC',
    'Ribbon Road': 'dRiR',
    'Super Bell Subway': 'dSBS',
    'Big Blue': 'dBB',
    
    // Golden Dash Cup (Booster Course Pass Wave 1)
    'Paris Promenade': 'bPP',
    'Toad Circuit': 'bTC',
    'Choco Mountain': 'bCMo',
    'Coconut Mall': 'bCMa',
    
    // Lucky Cat Cup (Booster Course Pass Wave 1)
    'Tokyo Blur': 'bTB',
    'Shroom Ridge': 'bSR',
    'Sky Garden': 'bSG',
    'Ninja Hideaway': 'bNH',
    
    // Turnip Cup (Booster Course Pass Wave 2)
    'New York Minute': 'bNYM',
    'Mario Circuit 3': 'bMC3',
    'Kalimari Desert': 'bKD',
    'Waluigi Pinball': 'bWP',
    
    // Propeller Cup (Booster Course Pass Wave 2)
    'Sydney Sprint': 'bSS',
    'Snow Land': 'bSL',
    'Mushroom Gorge': 'bMG',
    'Sky-High Sundae': 'bSHS',
    
    // Rock Cup (Booster Course Pass Wave 3)
    'London Loop': 'bLL',
    'Boo Lake': 'bBL',
    'Rock Rock Mountain': 'bRRM',
    'Maple Treeway': 'bMT',
    
    // Moon Cup (Booster Course Pass Wave 3)
    'Berlin Byways': 'bBB',
    'Peach Gardens': 'bPG',
    'Merry Mountain': 'bMM',
    'Rainbow Road (3DS)': 'bRR7',
    
    // Fruit Cup (Booster Course Pass Wave 4)
    'Amsterdam Drift': 'bAD',
    'Riverside Park': 'bRP',
    'DK Summit': 'bDKS',
    'Yoshi\'s Island': 'bYI',
    
    // Boomerang Cup (Booster Course Pass Wave 4)
    'Bangkok Rush': 'bBR',
    'Mario Circuit (DS)': 'bMC',
    'Waluigi Stadium': 'bWS',
    'Singapore Speedway': 'bSSy',
    
    // Feather Cup (Booster Course Pass Wave 5)
    'Athens Dash': 'bADa',
    'Daisy Cruiser': 'bDC',
    'Moonview Highway': 'bMH',
    'Squeaky Clean Sprint': 'bSQS',
    
    // Cherry Cup (Booster Course Pass Wave 5)
    'Los Angeles Laps': 'bLAL',
    'Sunset Wilds': 'bSW',
    'Koopa Cape': 'bKC',
    'Vancouver Velocity': 'bVV',
    
    // Acorn Cup (Booster Course Pass Wave 6)
    'Rome Avanti': 'bRA',
    'DK Mountain': 'bDKM',
    'Daisy Circuit': 'bDCt',
    'Piranha Plant Cove': 'bPPC',
    
    // Spiny Cup (Booster Course Pass Wave 6)
    'Madrid Drive': 'bMD',
    'Rosalina\'s Ice World': 'bRIW',
    'Bowser\'s Castle 3': 'bBC3',
    'Rainbow Road (Wii)': 'bRRW'
};

// Reverse mapping for track abbreviations to full names
export const MK8DX_ABBREVIATION_TO_TRACK = Object.fromEntries(
    Object.entries(MK8DX_TRACK_ABBREVIATIONS).map(([track, abbr]) => [abbr, track])
);

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
    'Crown City 2',
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
    'Peach Stadium 2',
    'Rainbow Road'
] as const;

// Simple abbreviations for MKWorld tracks
export const MKWORLD_TRACK_ABBREVIATIONS: Record<string, string> = {
    'Mario Bros. Circuit': 'MBC',
    'Crown City': 'CC1', 
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
    'Crown City 2': 'CC2',
    'Peach Stadium': 'PS1',
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
    'Mario Circuit': 'MC',
    'Peach Stadium 2': 'PS2',
    'Rainbow Road': 'RR'
};

// Reverse mapping for MKWorld
export const MKWORLD_ABBREVIATION_TO_TRACK = Object.fromEntries(
    Object.entries(MKWORLD_TRACK_ABBREVIATIONS).map(([track, abbr]) => [abbr, track])
);

export const TRACKS_BY_GAME = {
    mk8dx: MK8DX_TRACKS,
    mkworld: MKWORLD_TRACKS
} as const;

export const TRACK_ABBREVIATIONS_BY_GAME = {
    mk8dx: MK8DX_TRACK_ABBREVIATIONS,
    mkworld: MKWORLD_TRACK_ABBREVIATIONS
} as const;

export const ABBREVIATION_TO_TRACK_BY_GAME = {
    mk8dx: MK8DX_ABBREVIATION_TO_TRACK,
    mkworld: MKWORLD_ABBREVIATION_TO_TRACK
} as const;

export const ENGINE_CLASSES = {
    mk8dx: [150, 200],
    mkworld: [150] // Only 150cc for Mario Kart World
} as const;

// Helper functions for track name/abbreviation conversion
export function getTrackAbbreviation(game: GameId, trackName: string): string {
    return TRACK_ABBREVIATIONS_BY_GAME[game][trackName] || trackName;
}

export function getTrackFromAbbreviation(game: GameId, abbreviation: string): string {
    return ABBREVIATION_TO_TRACK_BY_GAME[game][abbreviation] || abbreviation;
}
