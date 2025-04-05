export function makeStats(tournaments) {
    const rostersMap = new Map();
    const playersMap = new Map();
    for (const tournament of tournaments) {
        for (const placement of tournament.placements) {
            if (tournament.is_squad) {
                for (const roster of placement.squad.rosters) {
                    const roster_id = roster.roster_id;
                    if (!rostersMap.has(roster_id)) {
                        rostersMap.set(roster_id, newRosterObject(roster))
                    }
                    const { gold, silver, bronze } = addMedals(placement.placement);
                    const r = rostersMap.get(roster_id);
                    r.gold += gold;
                    r.silver += silver;
                    r.bronze += bronze;
                    r.appearances++;
                }

                for (const player of placement.squad.players) {
                    const player_id = player.player_id;
                    if (!playersMap.has(player_id)) {
                        playersMap.set(player_id, newPlayerObject(player));
                    }
                    const { gold, silver, bronze } = addMedals(placement.placement);
                    const r = playersMap.get(player_id);
                    r.gold += gold;
                    r.silver += silver;
                    r.bronze += bronze;
                    r.appearances++;
                }
            }
        }
    }
    const rostersArray = Array.from(rostersMap, ([key, value]) => ({
        roster_id: key,
        name: value.name,
        tag: value.tag,
        color: value.color,
        gold: value.gold,
        silver: value.silver,
        bronze: value.bronze,
        appearances: value.appearances
    }));
    const playersArray = Array.from(playersMap, ([key, value]) => ({
        player_id: key,
        name: value.name,
        gold: value.gold,
        silver: value.silver,
        bronze: value.bronze,
        appearances: value.appearances
    }));
    addRankings(rostersArray);
    addRankings(playersArray);
    return {
        rostersArray: rostersArray,
        playersArray: playersArray
    };
}

function newRosterObject(roster) {
    return {
        roster_id: roster.roster_id,
        name: roster.roster_name,
        tag: roster.roster_tag,
        color: roster.team_color,
        gold: 0,
        silver: 0,
        bronze: 0,
        appearances: 0,
    };
}

function newPlayerObject(player) {
    return {
        player_id: player.player_id,
        name: player.name,
        gold: 0,
        silver: 0,
        bronze: 0,
        appearances: 0,
    };
}

function addMedals(placement) {
    let gold = 0;
    let silver = 0;
    let bronze = 0;
    switch (placement) {
        case 1:
            gold++;
            break;
        case 2:
            silver++;
            break;
        case 3:
            bronze++;
            break;
        default:
            break;
    }
    return { gold, silver, bronze };
}
function addRankings(array) {
    addMedalsRankings(array);
    addAppearanceRankings(array);
}

function addMedalsRankings(array) {
    array = sortByMedals(array);
    for (let i = 0; i < array.length; i++) {
        array[i].medals_placement = i + 1;
        if (i > 0 && array[i - 1].gold === array[i].gold && array[i - 1].silver === array[i].silver && array[i - 1].bronze === array[i].bronze) {
            array[i].medals_placement = array[i - 1].medals_placement;
        }
    }
    return array;
}

function addAppearanceRankings(array) {
    array = sortByAppearances(array);
    for (let i = 0; i < array.length; i++) {
        array[i].appearances_placement = i + 1;
        if (i > 0 && array[i - 1].appearances === array[i].appearances) {
            array[i].appearances_placement = array[i - 1].appearances_placement;
        }
    }
    console.log(array)
    return array;
}

export function sortByMedals(array) {
    return array.sort((a, b) => {
        if (a.gold !== b.gold) {
            return b.gold - a.gold;
        }
        if (a.silver !== b.silver) {
            return b.silver - a.silver
        };
        return b.bronze - a.bronze;
    });
}

export function sortByAppearances(array) {
    return array.sort((a, b) => {
        return b.appearances - a.appearances;
    })
}