import type { TeamRoster } from './team-roster';

export type Team = {
  id: number;
  name: string;
  tag: string;
  description: string;
  creation_date: number;
  language: string;
  color: number;
  logo: string;
  is_approved: string;
  is_historical: boolean;
  rosters: TeamRoster[];
};
