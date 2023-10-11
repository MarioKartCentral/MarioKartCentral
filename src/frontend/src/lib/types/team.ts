import type { TeamRoster } from './team-roster';
import type { PlayerInfo } from './player-info';

export type Team = {
  id: number;
  name: string;
  tag: string;
  description: string;
  creation_date: number;
  language: string;
  color: number;
  logo: string;
  approval_status: string;
  is_historical: boolean;
  rosters: TeamRoster[];
  managers: PlayerInfo[];
};
