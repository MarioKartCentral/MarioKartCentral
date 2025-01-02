import type { TournamentWithPlacements } from '$lib/types/tournament';
import type { TournamentSeriesPlacements } from '$lib/types/tournament-placement';

function addTeams(tournaments: TournamentWithPlacements[]) {
  const teams: TournamentSeriesPlacements[] = [];
  for (const tournament of tournaments) {
    console.log(tournament)
    if (tournament.placements) {
      for (const placement of tournament.placements) {
        let team_added = false;
        for (const team of teams) {
          if (placement.squad?.roster_id === team.id) {
            team_added = true;
          }
        }
        if (!team_added && placement.squad?.roster_id && placement.squad?.name && placement.squad?.tag) {
          const team_placement: TournamentSeriesPlacements = {
            id: placement.squad.roster_id,
            name: placement.squad.name,
            tag: placement.squad.tag,
            gold_medals: 0,
            silver_medals: 0,
            bronze_medals: 0,
            podiums: 0,
            finals: 0,
            participations: 0,
            medals_placement: 0,
            podiums_placement: 0,
            finals_placement: 0,
            participations_placement: 0
          };
          teams.push(team_placement);
        }
      }
    }
  }
  return teams;
}

function orderByPodiums(a: TournamentSeriesPlacements, b: TournamentSeriesPlacements) {
  if (a.gold_medals > b.gold_medals) {
    return -1;
  } else if (a.gold_medals < b.gold_medals) {
    return 1;
  } else if (a.silver_medals > b.silver_medals) {
    return -1;
  } else if (a.silver_medals < b.silver_medals) {
    return 1;
  } else if (a.bronze_medals > b.bronze_medals) {
    return -1;
  } else if (a.bronze_medals < b.bronze_medals) {
    return 1;
  } else {
    return 0;
  }
}

function addPlacements(teams: TournamentSeriesPlacements[], column: string) {
  if (teams.length > 0) {
    teams[0][column] = 1;
  }
  for (let i = 1; i < teams.length; i++) {
    if (orderByPodiums(teams[i - 1], teams[i]) === 0) {
      teams[i][column] = teams[i - 1][column];
    } else {
      teams[i][column] = i + 1;
    }
  }
  return teams;
}

function addMedails(teams: TournamentSeriesPlacements[], tournaments: TournamentWithPlacements[]) {
  for (const team of teams) {
    for (const tournament of tournaments) {
      for (const placement of tournament.placements) {
        if (placement.squad && placement.squad.roster_id === team.id) {
          team.participations += 1;
          if (placement.placement === 1) {
            team.gold_medals += 1;
            team.podiums += 1;
            team.finals += 1;
          }
          if (placement.placement === 2) {
            team.silver_medals += 1;
            team.podiums += 1;  
            team.finals += 1;
          }
          if (placement.placement === 3) {
            team.bronze_medals += 1;
            team.podiums += 1;
          }
        }
      }
    }
  }
  return teams;
}

export function makeMedalsRankings(tournaments: TournamentWithPlacements[]) {
  // get list of teams which participated in the tournament series
  const teams: TournamentSeriesPlacements[] = addTeams(tournaments);

  const teams_completed = addMedails(teams, tournaments);

  const teams_sorted_by_medals = teams_completed.sort(orderByPodiums);
  const teams_with_medals_placements = addPlacements(teams_sorted_by_medals, "medals_placement");

  const teams_sorted_by_podiums = teams_with_medals_placements.sort((a, b) => b.podiums - a.podiums);
  const teams_with_podiums_placements = addPlacements(teams_sorted_by_podiums, "podiums_placement");

  const teams_sorted_by_finals = teams_with_podiums_placements.sort((a, b) => b.finals - a.finals);
  const teams_with_finals_placements = addPlacements(teams_sorted_by_finals, "finals_placement");

  const team_sorted_by_participations = teams_with_finals_placements.sort((a, b) => b.participations - a.participations);
  const teams_with_participations_placements = addPlacements(team_sorted_by_participations, "participations_placement");

  console.log(teams_with_participations_placements);
  return teams_with_participations_placements;
}