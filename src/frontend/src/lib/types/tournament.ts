import type { CreateTournament } from './tournaments/create/create-tournament';
import type { TournamentPlacementList } from './tournament-placement';

export type Tournament = {
  id: number;
  series_name: string | null;
  series_url: string | null;
  series_description: string | null;
  series_ruleset: string | null;
} & CreateTournament;

export type TournamentWithPlacements = Tournament & {
  placements: TournamentPlacementList;
};
