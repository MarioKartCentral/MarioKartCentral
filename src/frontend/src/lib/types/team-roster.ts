import type { RosterPlayer } from './roster-player';
import type { RosterInvite } from './roster-invite';

export type TeamRoster = {
  id: number;
  team_id: number;
  game: string;
  mode: string;
  name: string;
  tag: string;
  creation_date: number;
  is_recruiting: boolean;
  is_active: boolean;
  approval_status: string;
  color: number;
  players: RosterPlayer[];
  invites: RosterInvite[];
};
