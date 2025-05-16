import type { TournamentWithPlacements } from "$lib/types/tournament";
import type { PlayerSeriesStats, RosterSeriesStats, SeriesStats, Medals } from "$lib/types/series-stats";

export function makeStats(tournaments: TournamentWithPlacements[]) {
  const rosterMap = new Map<number, RosterSeriesStats>();
  const playerMap = new Map<number, PlayerSeriesStats>();

  for (const tournament of tournaments) {
    for (const placement of tournament.placements) {

      const placementResult = placement.placement;
      if(placementResult === null) continue;
      for (const roster of placement.squad.rosters) {
        if(!rosterMap.has(roster.roster_id)) {
          rosterMap.set(roster.roster_id, {
            ...roster,
            gold: 0,
            silver: 0,
            bronze: 0,
            appearances: 0,
            medals_placement: 0,
            appearances_placement: 0,
          });
        }
        if (roster.roster_id !== null && roster.roster_id !== 0) {
          updateStats(rosterMap, roster.roster_id, placementResult);
        }
      }

      for (const player of placement.squad.players) {
        if(!playerMap.has(player.player_id)) {
          playerMap.set(player.player_id, {
            id: player.player_id, name: player.name, country_code: player.country_code,
            gold: 0, silver: 0, bronze: 0, appearances: 0, medals_placement: 0, appearances_placement: 0,
          });
        }
        updateStats(playerMap, player.player_id, placementResult);
      }
    }
  }

  const rostersArray: RosterSeriesStats[] = Array.from(rosterMap.values());
  const playersArray: PlayerSeriesStats[] = Array.from(playerMap.values());

  addRankings(rostersArray);
  addRankings(playersArray);

  return {
    roster_stats: rostersArray,
    player_stats: playersArray,
  };
}

// === Shared Utility Functions ===

function updateStats(map: Map<number, SeriesStats>, id: number, placement: number) {
  const obj = map.get(id);
  if(!obj) return;

  const { gold, silver, bronze } = getMedals(placement);

  obj.gold += gold;
  obj.silver += silver;
  obj.bronze += bronze;
  obj.appearances++;
}

// === Medal Helpers ===

const medalsCache = new Map<number, Medals>();

function getMedals(placement: number) {
  const cache_hit = medalsCache.get(placement);
  if(cache_hit) return cache_hit;

  const medals = { gold: 0, silver: 0, bronze: 0 };

  if (placement === 1) medals.gold++;
  else if (placement === 2) medals.silver++;
  else if (placement === 3) medals.bronze++;

  medalsCache.set(placement, medals);
  return medals;
}

// === Ranking Helpers ===

function addRankings(array: SeriesStats[]) {
  addMedalsRanking(array);
  addAppearancesRanking(array);
}

function addMedalsRanking(array: SeriesStats[]) {
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

function addAppearancesRanking(array: SeriesStats[]) {
  array.sort((a, b) => b.appearances - a.appearances);

  for (let i = 0; i < array.length; i++) {
    array[i].appearances_placement = i + 1;
    if (i > 0 && array[i].appearances === array[i - 1].appearances) {
      array[i].appearances_placement = array[i - 1].appearances_placement;
    }
  }
}

// === Sorting Utilities ===

export function compareMedals(a: SeriesStats, b: SeriesStats) {
  if (a.gold !== b.gold) return b.gold - a.gold;
  if (a.silver !== b.silver) return b.silver - a.silver;
  return b.bronze - a.bronze;
}

export function sortByMedals(array: SeriesStats[]) {
  return array.sort(compareMedals);
}

export function sortByAppearances(array: SeriesStats[]) {
  return array.sort((a, b) => b.appearances - a.appearances);
}
