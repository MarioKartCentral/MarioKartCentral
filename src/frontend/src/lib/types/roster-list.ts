import type { TeamRoster } from './team-roster';

export type RosterList = {
  rosters: TeamRoster[];
  count: number;
  page_count: number;
};
