export default function makeStats(tournaments) {
    console.log("makeStats");
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
                    const r = rostersMap.get(roster_id);
                    r.gold += gold;
                    r.silver += silver;
                    r.bronze += bronze;
                    r.participations++;
                }

                for (const player of placement.squad.players) {
                    const player_id = player.player_id;
                    if (!playersMap.has(player_id)) {
                        playersMap.set(player_id, newPlayerObject(player))
                    }
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
                    const r = playersMap.get(player_id);
                    r.gold += gold;
                    r.silver += silver;
                    r.bronze += bronze;
                    r.participations++;
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
        participations: value.participations
    }));
    const playersArray = Array.from(playersMap, ([key, value]) => ({
        player_id: key,
        name: value.name,
        gold: value.gold,
        silver: value.silver,
        bronze: value.bronze,
        participations: value.participations
    }));
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
        participations: 0,
    };
}

function newPlayerObject(player) {
    return {
        player_id: player.player_id,
        name: player.name,
        gold: 0,
        silver: 0,
        bronze: 0,
        participations: 0,
    };
}