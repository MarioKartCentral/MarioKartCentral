export function makeStats(tournaments) {
    const rostersMap = new Map();
    const playersMap = new Map();

    console.log('Tournaments:', tournaments);

    for (const tournament of tournaments) {
        for (const placement of tournament.placements) {
            const placementResult = placement.placement;
            for (const roster of placement.squad.rosters) {
                updateStats(rostersMap, roster.roster_id, () => newRosterObject(roster), placementResult);
            }

            for (const player of placement.squad.players) {
                updateStats(playersMap, player.player_id, () => newPlayerObject(player), placementResult);
            }
        }
    }

    const rostersArray = Array.from(rostersMap.entries()).map(([roster_id, value]) => ({
        ...value,
        roster_id
    }));

    const playersArray = Array.from(playersMap.entries()).map(([player_id, value]) => ({
        ...value,
        player_id
    }));

    addRankings(rostersArray);
    addRankings(playersArray);

    return {
        rostersArray,
        playersArray
    };
}

// === Shared Utility Functions ===

function updateStats(map, id, createFn, placement) {
    if (!map.has(id)) {
        map.set(id, createFn());
    }

    const { gold, silver, bronze } = getMedals(placement);
    const obj = map.get(id);

    obj.gold += gold;
    obj.silver += silver;
    obj.bronze += bronze;
    obj.appearances++;
}

function newRosterObject(roster) {
    return {
        name: roster.roster_name,
        tag: roster.roster_tag,
        color: roster.team_color,
        gold: 0,
        silver: 0,
        bronze: 0,
        appearances: 0
    };
}

function newPlayerObject(player) {
    return {
        name: player.name,
        country_code: player.country_code,
        gold: 0,
        silver: 0,
        bronze: 0,
        appearances: 0
    };
}

// === Medal Helpers ===

const medalsCache = new Map();

function getMedals(placement) {
    if (medalsCache.has(placement)) return medalsCache.get(placement);

    const medals = { gold: 0, silver: 0, bronze: 0 };

    if (placement === 1) medals.gold++;
    else if (placement === 2) medals.silver++;
    else if (placement === 3) medals.bronze++;

    medalsCache.set(placement, medals);
    return medals;
}

// === Ranking Helpers ===

function addRankings(array) {
    addMedalsRanking(array);
    addAppearancesRanking(array);
}

function addMedalsRanking(array) {
    array.sort(compareMedals);

    for (let i = 0; i < array.length; i++) {
        array[i].medals_placement = i + 1;
        if (
            i > 0 &&
            array[i].gold === array[i - 1].gold &&
            array[i].silver === array[i - 1].silver &&
            array[i].bronze === array[i - 1].bronze
        ) {
            array[i].medals_placement = array[i - 1].medals_placement;
        }
    }
}

function addAppearancesRanking(array) {
    array.sort((a, b) => b.appearances - a.appearances);

    for (let i = 0; i < array.length; i++) {
        array[i].appearances_placement = i + 1;
        if (i > 0 && array[i].appearances === array[i - 1].appearances) {
            array[i].appearances_placement = array[i - 1].appearances_placement;
        }
    }
}

// === Sorting Utilities ===

export function compareMedals(a, b) {
    if (a.gold !== b.gold) return b.gold - a.gold;
    if (a.silver !== b.silver) return b.silver - a.silver;
    return b.bronze - a.bronze;
}

export function sortByMedals(array) {
    return array.sort(compareMedals);
}

export function sortByAppearances(array) {
    return array.sort((a, b) => b.appearances - a.appearances);
}
