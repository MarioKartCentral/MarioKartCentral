import type { TournamentListItem } from './tournament-list-item';

export type TournamentList = {
  tournaments: TournamentListItem[];
  tournament_count: number;
  page_count: number;
};
